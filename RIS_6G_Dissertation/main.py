import numpy as np

from experiments import (
    run_geometry_baseline,
    run_ris_size_experiment,
    run_imperfect_csi_experiment,
    run_mobility_experiment,
    run_mobility_update_experiment
)

from plots import (
    plot_ris_size_results,
    plot_csi_results,
    plot_mobility_update_results
)

# --------------------------------------------------
# Random seed for reproducibility
# --------------------------------------------------

np.random.seed(42)

# --------------------------------------------------
# Baseline simulation parameters
# --------------------------------------------------

carrier_frequency_hz = 30e9
num_ris_elements = 16

transmit_power_dbm = 35
bandwidth_hz = 100e6

thermal_noise_density_dbm_hz = -174
noise_figure_db = 9


# --------------------------------------------------
# Physical geometry
# --------------------------------------------------

bs_position = np.array([
    0.0,
    0.0,
    10.0
])

ris_position = np.array([
    50.0,
    10.0,
    5.0
])

user_position = np.array([
    100.0,
    0.0,
    1.5
])


# --------------------------------------------------
# Run baseline experiment
# --------------------------------------------------

results = run_geometry_baseline(
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


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\nRIS 6G Geometry-Based Simulation")
print("--------------------------------")

print(
    "Carrier frequency:",
    carrier_frequency_hz / 1e9,
    "GHz"
)

print(
    "Wavelength:",
    round(results["wavelength"], 4),
    "m"
)

print(
    "RIS elements:",
    num_ris_elements
)

print(
    "RIS array:",
    f"{int(np.sqrt(num_ris_elements))} x "
    f"{int(np.sqrt(num_ris_elements))}"
)


print("\nGeometry")
print("--------")

print(
    "BS-to-User distance:",
    round(
        results["distance_bs_user"],
        2
    ),
    "m"
)

print(
    "BS-to-RIS element distance range:",
    round(
        np.min(results["distances_bs_ris"]),
        4
    ),
    "to",
    round(
        np.max(results["distances_bs_ris"]),
        4
    ),
    "m"
)

print(
    "RIS-to-User element distance range:",
    round(
        np.min(results["distances_ris_user"]),
        4
    ),
    "to",
    round(
        np.max(results["distances_ris_user"]),
        4
    ),
    "m"
)


print("\nChannel comparison")
print("------------------")

print(
    "Without RIS:",
    np.abs(results["h_direct"])
)

print(
    "RIS path:",
    np.abs(results["h_ris_path"])
)

print(
    "With RIS:",
    np.abs(results["h_effective"])
)


print("\nSNR comparison")
print("--------------")

print(
    "Noise power:",
    round(
        results["noise_power_dbm"],
        2
    ),
    "dBm"
)

print(
    "SNR without RIS:",
    round(
        results["snr_without_ris_db"],
        4
    ),
    "dB"
)

print(
    "SNR with RIS:",
    round(
        results["snr_with_ris_db"],
        4
    ),
    "dB"
)

print(
    "SNR improvement:",
    round(
        results["snr_improvement_db"],
        4
    ),
    "dB"
)


print("\nAchievable rate")
print("---------------")

print(
    "Without RIS:",
    round(
        results["rate_without_ris_bps"]
        / 1e6,
        2
    ),
    "Mbps"
)

print(
    "With RIS:",
    round(
        results["rate_with_ris_bps"]
        / 1e6,
        2
    ),
    "Mbps"
)

# --------------------------------------------------
# Experiment 1: RIS size sweep
# --------------------------------------------------

ris_sizes = [
    16,
    64,
    256,
    1024
]

size_results = run_ris_size_experiment(
    bs_position=bs_position,
    ris_position=ris_position,
    user_position=user_position,
    ris_sizes=ris_sizes,
    carrier_frequency_hz=carrier_frequency_hz,
    transmit_power_dbm=transmit_power_dbm,
    bandwidth_hz=bandwidth_hz,
    thermal_noise_density_dbm_hz=(
        thermal_noise_density_dbm_hz
    ),
    noise_figure_db=noise_figure_db,
    timing_repeats=100 
)

print("\nExperiment 1: RIS Size")
print("----------------------")

for result in size_results:

    print(
        "\nRIS elements:",
        result["ris_elements"]
    )

    print(
        "Array:",
        result["array_size"]
    )

    print(
        "SNR without RIS:",
        round(
            result["snr_without_ris_db"],
            4
        ),
        "dB"
    )

    print(
        "SNR with RIS:",
        round(
            result["snr_with_ris_db"],
            4
        ),
        "dB"
    )

    print(
        "SNR improvement:",
        round(
            result["snr_improvement_db"],
            4
        ),
        "dB"
    )

    print(
        "Achievable rate with RIS:",
        round(
            result["rate_with_ris_mbps"],
            2
        ),
        "Mbps"
    )

    print(
        "Median computation time:",
        round(
            result["median_execution_time_ms"],
            4
        ),
        "ms"
    )

    print(
        "Computation time IQR:",
        round(
            result["iqr_execution_time_ms"],
            4
        ),
        "ms"
    )

    print(
        "Q1 -Q3 range:",
        round(
            result["q1_execution_time_ms"],
            4
        ),
        "to",
        round(
            result["q3_execution_time_ms"],
            4
        ),
        "ms"
    )


# Create Experiment 1 plots
plot_ris_size_results(size_results)

# --------------------------------------------------
# Experiment 2: Imperfect CSI
# --------------------------------------------------

csi_nmse_levels = [
    None,   # Perfect CSI
    -30,
    -20,
    -10,
    0
]

csi_results = run_imperfect_csi_experiment(
    bs_position=bs_position,
    ris_position=ris_position,
    user_position=user_position,
    csi_nmse_levels=csi_nmse_levels,
    num_trials=1000,
    num_ris_elements=1024,
    carrier_frequency_hz=carrier_frequency_hz,
    transmit_power_dbm=transmit_power_dbm,
    bandwidth_hz=bandwidth_hz,
    thermal_noise_density_dbm_hz=(
        thermal_noise_density_dbm_hz
    ),
    noise_figure_db=noise_figure_db
)

print("\nExperiment 2: Imperfect CSI")
print("---------------------------")

for result in csi_results:

    print(
        "\nCSI quality:",
        result["csi_label"]
    )

    print(
        "Average SNR with RIS:",
        round(
            result["snr_with_ris_db"],
            4
        ),
        "dB"
    )

    print(
        "SNR improvement:",
        round(
            result["snr_improvement_db"],
            4
        ),
        "dB"
    )

    print(
        "Achievable rate:",
        round(
            result["rate_with_ris_mbps"],
            2
        ),
        "Mbps"
    )

    # Create Experiment 2 plots
plot_csi_results(csi_results)

# --------------------------------------------------
# Experiment 3: User mobility
# --------------------------------------------------

user_speeds = [
    0,
    1,
    5,
    15
]

mobility_results = run_mobility_experiment(
    bs_position=bs_position,
    ris_position=ris_position,
    initial_user_position=user_position,
    user_speeds=user_speeds,
    num_ris_elements=1024,
    carrier_frequency_hz=carrier_frequency_hz,
    transmit_power_dbm=transmit_power_dbm,
    bandwidth_hz=bandwidth_hz,
    thermal_noise_density_dbm_hz=(
        thermal_noise_density_dbm_hz
    ),
    noise_figure_db=noise_figure_db,
    simulation_duration=1.0,
    time_step=0.01,
    ris_update_interval=0.1
)

print("\nExperiment 3: User Mobility")
print("---------------------------")

for result in mobility_results:

    print(
        "\nUser speed:",
        result["speed_mps"],
        "m/s"
    )

    print(
        "Average SNR without RIS:",
        round(
            result["average_snr_without_ris_db"],
            4
        ),
        "dB"
    )

    print(
        "Average SNR with RIS:",
        round(
            result["average_snr_with_ris_db"],
            4
        ),
        "dB"
    )

    print(
        "Average SNR improvement:",
        round(
            result["average_snr_improvement_db"],
            4
        ),
        "dB"
    )

    print(
        "Average achievable rate:",
        round(
            result["average_rate_with_ris_mbps"],
            2
        ),
        "Mbps"
    )

# --------------------------------------------------
# Experiment 3B: Mobility vs RIS update interval
# --------------------------------------------------

user_speeds = [
    1,
    5,
    15
]

update_intervals = [
    0.001,
    0.005,
    0.01,
    0.05,
    0.1
]

mobility_update_results = run_mobility_update_experiment(
    bs_position=bs_position,
    ris_position=ris_position,
    initial_user_position=user_position,
    user_speeds=user_speeds,
    update_intervals=update_intervals,
    num_ris_elements=1024,
    carrier_frequency_hz=carrier_frequency_hz,
    transmit_power_dbm=transmit_power_dbm,
    bandwidth_hz=bandwidth_hz,
    thermal_noise_density_dbm_hz=(
        thermal_noise_density_dbm_hz
    ),
    noise_figure_db=noise_figure_db,
    simulation_duration=1.0,
    time_step=0.001
)

print("\nExperiment 3B: Mobility vs RIS Update Interval")
print("----------------------------------------------")

for result in mobility_update_results:

    print(
        "\nSpeed:",
        result["speed_mps"],
        "m/s"
    )

    print(
        "RIS update interval:",
        result["update_interval_ms"],
        "ms"
    )

    print(
        "Average SNR improvement:",
        round(
            result["average_snr_improvement_db"],
            4
        ),
        "dB"
    )

    print(
        "Average achievable rate:",
        round(
            result["average_rate_with_ris_mbps"],
            2
        ),
        "Mbps"
    )

# Create Experiment 3B plots
plot_mobility_update_results(
    mobility_update_results
)