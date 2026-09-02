import numpy as np


def umi_los_path_loss(distance_3d, carrier_frequency_ghz=30.0):
    """
    3GPP TR 38.901 UMi Street Canyon LOS path-loss model.

    Parameters
    ----------
    distance_3d : float
        3D transmitter-to-receiver distance in metres.

    carrier_frequency_ghz : float
        Carrier frequency in GHz.

    Returns
    -------
    path_loss_db : float
        Path loss in dB.
    """

    if distance_3d < 10:
        raise ValueError(
            "UMi LOS model requires distance >= 10 metres."
        )

    path_loss_db = (
        32.4
        + 21 * np.log10(distance_3d)
        + 20 * np.log10(carrier_frequency_ghz)
    )

    return path_loss_db


def rayleigh_channel(
    num_elements=1,
    distance=10.0,
    carrier_frequency_ghz=30.0
):
    """
    Generate a complex Rayleigh fading channel with
    3GPP UMi Street Canyon LOS large-scale path loss.

    Parameters
    ----------
    num_elements : int
        Number of channel coefficients.

    distance : float
        3D link distance in metres.

    carrier_frequency_ghz : float
        Carrier frequency in GHz.

    Returns
    -------
    channel : numpy.ndarray
        Complex channel coefficients including path loss.
    """

    # Small-scale Rayleigh fading
    real_part = np.random.randn(num_elements)
    imaginary_part = np.random.randn(num_elements)

    small_scale_fading = (
        real_part + 1j * imaginary_part
    ) / np.sqrt(2)

    # 3GPP UMi LOS path loss
    path_loss_db = umi_los_path_loss(
        distance_3d=distance,
        carrier_frequency_ghz=carrier_frequency_ghz
    )

    # Convert path loss from dB to linear power gain
    path_gain_linear = 10 ** (-path_loss_db / 10)

    # Channel amplitude scales with square root of power gain
    channel = (
        np.sqrt(path_gain_linear)
        * small_scale_fading
    )

    return channel

def geometry_channel(
    transmitter_position,
    receiver_positions,
    carrier_frequency_hz=30e9
):
    """
    Generate deterministic geometry-based LOS channel coefficients.

    Parameters
    ----------
    transmitter_position : numpy.ndarray
        Position of the transmitter [x, y, z] in metres.

    receiver_positions : numpy.ndarray
        One or more receiver positions.
        Shape may be (3,) for one receiver or (N, 3) for N receivers.

    carrier_frequency_hz : float
        Carrier frequency in Hz.

    Returns
    -------
    channel : numpy.ndarray
        Complex channel coefficients.

    distances : numpy.ndarray
        3D propagation distances in metres.
    """

    speed_of_light = 3e8

    wavelength = (
        speed_of_light / carrier_frequency_hz
    )

    # Ensure receiver_positions is always a 2D array
    receiver_positions = np.atleast_2d(
        receiver_positions
    )

    # Calculate distance from transmitter
    # to every receiver position
    differences = (
        receiver_positions
        - transmitter_position
    )

    distances = np.linalg.norm(
        differences,
        axis=1
    )

    carrier_frequency_ghz = (
        carrier_frequency_hz / 1e9
    )

    # Calculate 3GPP UMi LOS path loss for each link
    path_loss_db = np.array([
        umi_los_path_loss(
            distance,
            carrier_frequency_ghz
        )
        for distance in distances
    ])

    # Convert path loss to linear amplitude gain
    amplitude_gain = 10 ** (
        -path_loss_db / 20
    )

    # Propagation phase caused by travelled distance
    propagation_phase = (
        -2
        * np.pi
        * distances
        / wavelength
    )

    channel = (
        amplitude_gain
        * np.exp(
            1j * propagation_phase
        )
    )

    return channel, distances