import numpy as np
import time

from channel_model import geometry_channel

from ris_model import (
    create_ris_positions,
    optimal_ris_phases,
    effective_channel
)


def calculate_noise_power_dbm(
    bandwidth_hz=100e6,
    thermal_noise_density_dbm_hz=-174,
    noise_figure_db=9
):
    """
    Calculate total receiver noise power in dBm.
    """

    noise_power_dbm = (
        thermal_noise_density_dbm_hz
        + 10 * np.log10(bandwidth_hz)
        + noise_figure_db
    )

    return noise_power_dbm


def run_geometry_baseline(
    bs_position,
    ris_position,
    user_position,
    num_ris_elements=16,
    carrier_frequency_hz=30e9,
    transmit_power_dbm=35,
    bandwidth_hz=100e6,
    thermal_noise_density_dbm_hz=-174,
    noise_figure_db=9
):
    """
    Run one geometry-based RIS simulation.
    """

    speed_of_light = 3e8

    wavelength = (
        speed_of_light
        / carrier_frequency_hz
    )

    # Create physical RIS
    ris_element_positions = create_ris_positions(
        ris_position,
        num_ris_elements,
        wavelength
    )

    # BS -> RIS elements
    h_bs_ris, distances_bs_ris = geometry_channel(
        transmitter_position=bs_position,
        receiver_positions=ris_element_positions,
        carrier_frequency_hz=carrier_frequency_hz
    )

    # RIS elements -> User
    # Reciprocity allows UE -> RIS geometry calculation
    h_ris_user, distances_ris_user = geometry_channel(
        transmitter_position=user_position,
        receiver_positions=ris_element_positions,
        carrier_frequency_hz=carrier_frequency_hz
    )

    # Direct BS -> User
    h_direct, distance_bs_user = geometry_channel(
        transmitter_position=bs_position,
        receiver_positions=user_position,
        carrier_frequency_hz=carrier_frequency_hz
    )

    # RIS phase optimisation
    ris_phases = optimal_ris_phases(
        h_bs_ris,
        h_ris_user,
        h_direct
    )

    # Effective channel
    h_effective, h_ris_path = effective_channel(
        h_direct,
        h_bs_ris,
        h_ris_user,
        ris_phases
    )

    # Noise power
    noise_power_dbm = calculate_noise_power_dbm(
        bandwidth_hz,
        thermal_noise_density_dbm_hz,
        noise_figure_db
    )

    # Convert dBm to watts
    transmit_power_watts = 10 ** (
        (transmit_power_dbm - 30) / 10
    )

    noise_power_watts = 10 ** (
        (noise_power_dbm - 30) / 10
    )

    # Received powers
    received_power_without_ris = (
        transmit_power_watts
        * np.abs(h_direct[0]) ** 2
    )

    received_power_with_ris = (
        transmit_power_watts
        * np.abs(h_effective) ** 2
    )

    # Linear SNR
    snr_without_ris = (
        received_power_without_ris
        / noise_power_watts
    )

    snr_with_ris = (
        received_power_with_ris
        / noise_power_watts
    )

    # SNR in dB
    snr_without_ris_db = (
        10 * np.log10(snr_without_ris)
    )

    snr_with_ris_db = (
        10 * np.log10(snr_with_ris)
    )

    snr_improvement_db = (
        snr_with_ris_db
        - snr_without_ris_db
    )

    # Achievable rate
    achievable_rate_without_ris = (
        bandwidth_hz
        * np.log2(1 + snr_without_ris)
    )

    achievable_rate_with_ris = (
        bandwidth_hz
        * np.log2(1 + snr_with_ris)
    )

    return {
        "wavelength": wavelength,
        "ris_element_positions": ris_element_positions,

        "distance_bs_user": distance_bs_user[0],
        "distances_bs_ris": distances_bs_ris,
        "distances_ris_user": distances_ris_user,

        "h_direct": h_direct[0],
        "h_ris_path": h_ris_path,
        "h_effective": h_effective,

        "noise_power_dbm": noise_power_dbm,

        "snr_without_ris_db": snr_without_ris_db,
        "snr_with_ris_db": snr_with_ris_db,
        "snr_improvement_db": snr_improvement_db,

        "rate_without_ris_bps": achievable_rate_without_ris,
        "rate_with_ris_bps": achievable_rate_with_ris
    }

def run_ris_size_experiment(
    bs_position,
    ris_position,
    user_position,
    ris_sizes,
    carrier_frequency_hz=30e9,
    transmit_power_dbm=35,
    bandwidth_hz=100e6,
    thermal_noise_density_dbm_hz=-174,
    noise_figure_db=9,
    timing_repeats=20
):
    """
    Evaluate RIS-assisted performance for different RIS sizes
    and measure average computation time.
    """

    results = []

    for num_ris_elements in ris_sizes:

        execution_times = []

        baseline_result = None

        # Repeat calculation to obtain a more stable
        # estimate of execution time
        for _ in range(timing_repeats):

            start_time = time.perf_counter()

            current_result = run_geometry_baseline(
                bs_position=bs_position,
                ris_position=ris_position,
                user_position=user_position,
                num_ris_elements=num_ris_elements,
                carrier_frequency_hz=carrier_frequency_hz,
                transmit_power_dbm=transmit_power_dbm,
                bandwidth_hz=bandwidth_hz,
                thermal_noise_density_dbm_hz=(
                    thermal_noise_density_dbm_hz
                ),
                noise_figure_db=noise_figure_db
            )

            end_time = time.perf_counter()

            execution_times.append(
                end_time - start_time
            )

            # Keep one result for performance values
            baseline_result = current_result

        median_execution_time = np.median(
            execution_times
        )

        q1_execution_time = np.percentile(
            execution_times, 25
        )

        q3_execution_time = np.percentile(
            execution_times, 75
        )

        iqr_execution_time = (
            q3_execution_time - q1_execution_time
        )

        side_length = int(
            np.sqrt(num_ris_elements)
        )

        results.append({
            "ris_elements": num_ris_elements,

            "array_size":
                f"{side_length} x {side_length}",

            "snr_without_ris_db":
                baseline_result[
                    "snr_without_ris_db"
                ],

            "snr_with_ris_db":
                baseline_result[
                    "snr_with_ris_db"
                ],

            "snr_improvement_db":
                baseline_result[
                    "snr_improvement_db"
                ],

            "rate_without_ris_mbps":
                baseline_result[
                    "rate_without_ris_bps"
                ] / 1e6,

            "rate_with_ris_mbps":
                baseline_result[
                    "rate_with_ris_bps"
                ] / 1e6,

            "median_execution_time_ms": median_execution_time * 1000,
            "q1_execution_time_ms": q1_execution_time * 1000,
            "q3_execution_time_ms": q3_execution_time * 1000,
            "iqr_execution_time_ms": iqr_execution_time * 1000
        })

    return results

def add_csi_error(true_channel, nmse_db):
    """
    Add complex Gaussian estimation error to a true channel.

    Parameters
    ----------
    true_channel : numpy.ndarray
        Actual channel coefficients.

    nmse_db : float or None
        Normalised mean square error in dB.
        None represents perfect CSI.

    Returns
    -------
    estimated_channel : numpy.ndarray
        Imperfect channel estimate.
    """

    true_channel = np.asarray(true_channel)

    if nmse_db is None:
        return true_channel.copy()

    # Average true-channel power
    channel_power = np.mean(
        np.abs(true_channel) ** 2
    )

    # Convert NMSE from dB to linear scale
    nmse_linear = 10 ** (
        nmse_db / 10
    )

    # Required error power
    error_power = (
        channel_power
        * nmse_linear
    )

    # Complex Gaussian estimation error
    error = np.sqrt(
        error_power / 2
    ) * (
        np.random.randn(*true_channel.shape)
        + 1j
        * np.random.randn(*true_channel.shape)
    )

    estimated_channel = (
        true_channel + error
    )

    return estimated_channel

def run_imperfect_csi_experiment(
    bs_position,
    ris_position,
    user_position,
    csi_nmse_levels,
    num_trials=1000,
    num_ris_elements=1024,
    carrier_frequency_hz=30e9,
    transmit_power_dbm=35,
    bandwidth_hz=100e6,
    thermal_noise_density_dbm_hz=-174,
    noise_figure_db=9
):
    """
    Evaluate RIS performance under imperfect CSI.

    RIS phase shifts are calculated using estimated
    channels, while performance is evaluated using
    the true physical channels.
    """

    speed_of_light = 3e8

    wavelength = (
        speed_of_light
        / carrier_frequency_hz
    )

    # --------------------------------------------------
    # Generate true physical geometry
    # --------------------------------------------------

    ris_element_positions = create_ris_positions(
        ris_position,
        num_ris_elements,
        wavelength
    )

    # True BS -> RIS channel
    h_bs_ris_true, _ = geometry_channel(
        transmitter_position=bs_position,
        receiver_positions=ris_element_positions,
        carrier_frequency_hz=carrier_frequency_hz
    )

    # True RIS -> User channel
    h_ris_user_true, _ = geometry_channel(
        transmitter_position=user_position,
        receiver_positions=ris_element_positions,
        carrier_frequency_hz=carrier_frequency_hz
    )

    # True direct channel
    h_direct_true, _ = geometry_channel(
        transmitter_position=bs_position,
        receiver_positions=user_position,
        carrier_frequency_hz=carrier_frequency_hz
    )

    # --------------------------------------------------
    # Power parameters
    # --------------------------------------------------

    noise_power_dbm = calculate_noise_power_dbm(
        bandwidth_hz,
        thermal_noise_density_dbm_hz,
        noise_figure_db
    )

    transmit_power_watts = 10 ** (
        (transmit_power_dbm - 30) / 10
    )

    noise_power_watts = 10 ** (
        (noise_power_dbm - 30) / 10
    )

    # Baseline direct-link performance
    received_power_without_ris = (
        transmit_power_watts
        * np.abs(h_direct_true[0]) ** 2
    )

    snr_without_ris = (
        received_power_without_ris
        / noise_power_watts
    )

    snr_without_ris_db = (
        10 * np.log10(snr_without_ris)
    )

    results = []

    # --------------------------------------------------
    # Test each CSI quality
    # --------------------------------------------------

    for nmse_db in csi_nmse_levels:

        snr_trials_db = []
        rate_trials_mbps = []

        for _ in range(num_trials):

            # Estimated CSI available to RIS controller
            h_bs_ris_est = add_csi_error(
                h_bs_ris_true,
                nmse_db
            )

            h_ris_user_est = add_csi_error(
                h_ris_user_true,
                nmse_db
            )

            h_direct_est = add_csi_error(
                h_direct_true,
                nmse_db
            )

            # Configure RIS using ESTIMATED channels
            estimated_phases = optimal_ris_phases(
                h_bs_ris_est,
                h_ris_user_est,
                h_direct_est
            )

            # Evaluate those phase shifts using TRUE channels
            h_effective_true, _ = effective_channel(
                h_direct_true,
                h_bs_ris_true,
                h_ris_user_true,
                estimated_phases
            )

            received_power_with_ris = (
                transmit_power_watts
                * np.abs(h_effective_true) ** 2
            )

            snr_with_ris = (
                received_power_with_ris
                / noise_power_watts
            )

            snr_with_ris_db = (
                10
                * np.log10(snr_with_ris)
            )

            achievable_rate_mbps = (
                bandwidth_hz
                * np.log2(
                    1 + snr_with_ris
                )
                / 1e6
            )

            snr_trials_db.append(
                snr_with_ris_db
            )

            rate_trials_mbps.append(
                achievable_rate_mbps
            )

        average_snr_db = np.mean(
            snr_trials_db
        )

        average_rate_mbps = np.mean(
            rate_trials_mbps
        )

        results.append({
            "nmse_db": nmse_db,
            "csi_label": (
                "Perfect CSI"
                if nmse_db is None
                else f"{nmse_db} dB"
            ),
            "snr_without_ris_db": (
                snr_without_ris_db
            ),
            "snr_with_ris_db": (
                average_snr_db
            ),
            "snr_improvement_db": (
                average_snr_db
                - snr_without_ris_db
            ),
            "rate_with_ris_mbps": (
                average_rate_mbps
            )
        })

    return results

def run_mobility_experiment(
    bs_position,
    ris_position,
    initial_user_position,
    user_speeds,
    num_ris_elements=1024,
    carrier_frequency_hz=30e9,
    transmit_power_dbm=35,
    bandwidth_hz=100e6,
    thermal_noise_density_dbm_hz=-174,
    noise_figure_db=9,
    simulation_duration=1.0,
    time_step=0.01,
    ris_update_interval=0.1
):
    """
    Evaluate RIS performance under user mobility.

    The user moves along the y-axis.
    RIS phase shifts are updated periodically and
    remain fixed between updates.
    """

    speed_of_light = 3e8
    wavelength = speed_of_light / carrier_frequency_hz

    # Create physical RIS
    ris_element_positions = create_ris_positions(
        ris_position,
        num_ris_elements,
        wavelength
    )

    # Power parameters
    noise_power_dbm = calculate_noise_power_dbm(
        bandwidth_hz,
        thermal_noise_density_dbm_hz,
        noise_figure_db
    )

    transmit_power_watts = 10 ** (
        (transmit_power_dbm - 30) / 10
    )

    noise_power_watts = 10 ** (
        (noise_power_dbm - 30) / 10
    )

    # Time points
    time_values = np.arange(
        0,
        simulation_duration + time_step,
        time_step
    )

    results = []

    # --------------------------------------------------
    # Test each user speed
    # --------------------------------------------------

    for speed in user_speeds:

        snr_with_ris_values = []
        snr_without_ris_values = []
        rate_with_ris_values = []

        current_ris_phases = None
        last_update_time = -ris_update_interval

        for current_time in time_values:

            # User moves along positive y-direction
            current_user_position = np.array([
                initial_user_position[0],
                initial_user_position[1]
                + speed * current_time,
                initial_user_position[2]
            ])

            # True BS -> RIS channels
            h_bs_ris_true, _ = geometry_channel(
                transmitter_position=bs_position,
                receiver_positions=ris_element_positions,
                carrier_frequency_hz=carrier_frequency_hz
            )

            # True RIS -> moving User channels
            h_ris_user_true, _ = geometry_channel(
                transmitter_position=current_user_position,
                receiver_positions=ris_element_positions,
                carrier_frequency_hz=carrier_frequency_hz
            )

            # True direct BS -> User channel
            h_direct_true, _ = geometry_channel(
                transmitter_position=bs_position,
                receiver_positions=current_user_position,
                carrier_frequency_hz=carrier_frequency_hz
            )

            # --------------------------------------------------
            # RIS controller update
            # --------------------------------------------------

            if (
                current_ris_phases is None
                or current_time - last_update_time
                >= ris_update_interval - 1e-12
            ):
                current_ris_phases = optimal_ris_phases(
                    h_bs_ris_true,
                    h_ris_user_true,
                    h_direct_true
                )

                last_update_time = current_time

            # --------------------------------------------------
            # Evaluate current channel using most recent RIS phases
            # --------------------------------------------------

            h_effective, _ = effective_channel(
                h_direct_true,
                h_bs_ris_true,
                h_ris_user_true,
                current_ris_phases
            )

            # Received powers
            received_power_without_ris = (
                transmit_power_watts
                * np.abs(h_direct_true[0]) ** 2
            )

            received_power_with_ris = (
                transmit_power_watts
                * np.abs(h_effective) ** 2
            )

            # Linear SNR
            snr_without_ris = (
                received_power_without_ris
                / noise_power_watts
            )

            snr_with_ris = (
                received_power_with_ris
                / noise_power_watts
            )

            # SNR in dB
            snr_without_ris_db = (
                10 * np.log10(snr_without_ris)
            )

            snr_with_ris_db = (
                10 * np.log10(snr_with_ris)
            )

            # Achievable rate
            rate_with_ris_mbps = (
                bandwidth_hz
                * np.log2(1 + snr_with_ris)
                / 1e6
            )

            snr_without_ris_values.append(
                snr_without_ris_db
            )

            snr_with_ris_values.append(
                snr_with_ris_db
            )

            rate_with_ris_values.append(
                rate_with_ris_mbps
            )

        # --------------------------------------------------
        # Average performance over movement period
        # --------------------------------------------------

        average_snr_without_ris = np.mean(
            snr_without_ris_values
        )

        average_snr_with_ris = np.mean(
            snr_with_ris_values
        )

        average_rate_with_ris = np.mean(
            rate_with_ris_values
        )

        results.append({
            "speed_mps": speed,

            "average_snr_without_ris_db":
                average_snr_without_ris,

            "average_snr_with_ris_db":
                average_snr_with_ris,

            "average_snr_improvement_db":
                average_snr_with_ris
                - average_snr_without_ris,

            "average_rate_with_ris_mbps":
                average_rate_with_ris,

            "time_values":
                time_values,

            "snr_with_ris_over_time":
                np.array(snr_with_ris_values),

            "snr_without_ris_over_time":
                np.array(snr_without_ris_values)
        })

    return results

def run_mobility_update_experiment(
    bs_position,
    ris_position,
    initial_user_position,
    user_speeds,
    update_intervals,
    num_ris_elements=1024,
    carrier_frequency_hz=30e9,
    transmit_power_dbm=35,
    bandwidth_hz=100e6,
    thermal_noise_density_dbm_hz=-174,
    noise_figure_db=9,
    simulation_duration=1.0,
    time_step=0.001
):
    """
    Evaluate RIS performance for different user speeds
    and RIS update intervals.
    """

    speed_of_light = 3e8
    wavelength = speed_of_light / carrier_frequency_hz

    ris_element_positions = create_ris_positions(
        ris_position,
        num_ris_elements,
        wavelength
    )

    noise_power_dbm = calculate_noise_power_dbm(
        bandwidth_hz,
        thermal_noise_density_dbm_hz,
        noise_figure_db
    )

    transmit_power_watts = 10 ** (
        (transmit_power_dbm - 30) / 10
    )

    noise_power_watts = 10 ** (
        (noise_power_dbm - 30) / 10
    )

    time_values = np.arange(
        0,
        simulation_duration + time_step,
        time_step
    )

    results = []

    for speed in user_speeds:

        for update_interval in update_intervals:

            snr_with_ris_values = []
            snr_without_ris_values = []
            rate_with_ris_values = []

            current_ris_phases = None
            last_update_time = -update_interval

            for current_time in time_values:

                current_user_position = np.array([
                    initial_user_position[0],
                    initial_user_position[1] + speed * current_time,
                    initial_user_position[2]
                ])

                # True BS -> RIS channel
                h_bs_ris_true, _ = geometry_channel(
                    transmitter_position=bs_position,
                    receiver_positions=ris_element_positions,
                    carrier_frequency_hz=carrier_frequency_hz
                )

                # True RIS -> User channel
                h_ris_user_true, _ = geometry_channel(
                    transmitter_position=current_user_position,
                    receiver_positions=ris_element_positions,
                    carrier_frequency_hz=carrier_frequency_hz
                )

                # True direct BS -> User channel
                h_direct_true, _ = geometry_channel(
                    transmitter_position=bs_position,
                    receiver_positions=current_user_position,
                    carrier_frequency_hz=carrier_frequency_hz
                )

                # Update RIS phases periodically
                if (
                    current_ris_phases is None
                    or current_time - last_update_time
                    >= update_interval - 1e-12
                ):
                    current_ris_phases = optimal_ris_phases(
                        h_bs_ris_true,
                        h_ris_user_true,
                        h_direct_true
                    )

                    last_update_time = current_time

                # Evaluate with current stored RIS phases
                h_effective, _ = effective_channel(
                    h_direct_true,
                    h_bs_ris_true,
                    h_ris_user_true,
                    current_ris_phases
                )

                received_power_without_ris = (
                    transmit_power_watts
                    * np.abs(h_direct_true[0]) ** 2
                )

                received_power_with_ris = (
                    transmit_power_watts
                    * np.abs(h_effective) ** 2
                )

                snr_without_ris = (
                    received_power_without_ris
                    / noise_power_watts
                )

                snr_with_ris = (
                    received_power_with_ris
                    / noise_power_watts
                )

                snr_without_ris_db = (
                    10 * np.log10(snr_without_ris)
                )

                snr_with_ris_db = (
                    10 * np.log10(snr_with_ris)
                )

                rate_with_ris_mbps = (
                    bandwidth_hz
                    * np.log2(1 + snr_with_ris)
                    / 1e6
                )

                snr_without_ris_values.append(
                    snr_without_ris_db
                )

                snr_with_ris_values.append(
                    snr_with_ris_db
                )

                rate_with_ris_values.append(
                    rate_with_ris_mbps
                )

            average_without_ris = np.mean(
                snr_without_ris_values
            )

            average_with_ris = np.mean(
                snr_with_ris_values
            )

            average_rate = np.mean(
                rate_with_ris_values
            )

            results.append({
                "speed_mps": speed,
                "update_interval_s": update_interval,
                "update_interval_ms": update_interval * 1000,
                "average_snr_without_ris_db":
                    average_without_ris,
                "average_snr_with_ris_db":
                    average_with_ris,
                "average_snr_improvement_db":
                    average_with_ris
                    - average_without_ris,
                "average_rate_with_ris_mbps":
                    average_rate
            })

    return results