import numpy as np


def create_ris_positions(ris_centre, num_elements, wavelength):
    """
    Create a square planar RIS with half-wavelength spacing.
    """

    side_length = int(np.sqrt(num_elements))

    if side_length ** 2 != num_elements:
        raise ValueError(
            "Number of RIS elements must be a perfect square."
        )

    element_spacing = wavelength / 2
    positions = []

    offset = (side_length - 1) / 2

    for row in range(side_length):
        for column in range(side_length):

            y_offset = (column - offset) * element_spacing
            z_offset = (row - offset) * element_spacing

            element_position = np.array([
                ris_centre[0],
                ris_centre[1] + y_offset,
                ris_centre[2] + z_offset
            ])

            positions.append(element_position)

    return np.array(positions)


def optimal_ris_phases(
    h_bs_ris,
    h_ris_user,
    h_direct
):
    """
    Configure the RIS so reflected contributions align
    with the direct BS-to-user channel.
    """

    cascaded_channel = h_bs_ris * h_ris_user

    direct_phase = np.angle(
        np.ravel(h_direct)[0]
    )

    phase_angles = (
        direct_phase
        - np.angle(cascaded_channel)
    )

    phase_shifts = np.exp(
        1j * phase_angles
    )

    return phase_shifts


def effective_channel(
    h_direct,
    h_bs_ris,
    h_ris_user,
    ris_phases
):
    """
    Calculate the total channel consisting of the
    direct path and RIS-assisted path.
    """

    ris_path = np.sum(
        h_bs_ris
        * ris_phases
        * h_ris_user
    )

    direct_channel = np.ravel(
        h_direct
    )[0]

    total_channel = (
        direct_channel
        + ris_path
    )

    return total_channel, ris_path