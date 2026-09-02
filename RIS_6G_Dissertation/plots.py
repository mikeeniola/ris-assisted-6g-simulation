def plot_ris_size_results(size_results):
    """
    Create and save plots for the RIS size experiment.
    """

    import os
    import matplotlib.pyplot as plt

    os.makedirs("results", exist_ok=True)

    # Extract results
    ris_elements = [
        result["ris_elements"]
        for result in size_results
    ]

    snr_improvement = [
        result["snr_improvement_db"]
        for result in size_results
    ]

    achievable_rate = [
        result["rate_with_ris_mbps"]
        for result in size_results
    ]

    median_computation_times = [
        result["median_execution_time_ms"]
        for result in size_results
    ]

    q1_computation_times = [
        result["q1_execution_time_ms"]
        for result in size_results
    ]

    q3_computation_times = [
        result["q3_execution_time_ms"]
        for result in size_results
    ]

    # Calculate asymmetric IQR error bars
    lower_errors = [
        median - q1
        for median, q1 in zip(
            median_computation_times,
            q1_computation_times
        )
    ]

    upper_errors = [
        q3 - median
        for median, q3 in zip(
            median_computation_times,
            q3_computation_times
        )
    ]

    # ----------------------------------------------
    # Figure 1: RIS size vs SNR improvement
    # ----------------------------------------------

    plt.figure()

    plt.plot(
        ris_elements,
        snr_improvement,
        marker="o"
    )

    plt.xlabel("Number of RIS Elements")
    plt.ylabel("SNR Improvement (dB)")
    plt.title("Effect of RIS Size on SNR Improvement")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "results/ris_size_vs_snr_improvement.png",
        dpi=300
    )

    # ----------------------------------------------
    # Figure 2: RIS size vs achievable rate
    # ----------------------------------------------

    plt.figure()

    plt.plot(
        ris_elements,
        achievable_rate,
        marker="o"
    )

    plt.xlabel("Number of RIS Elements")
    plt.ylabel("Achievable Rate (Mbps)")
    plt.title("Effect of RIS Size on Achievable Rate")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "results/ris_size_vs_achievable_rate.png",
        dpi=300
    )

    # ----------------------------------------------
    # Figure 3: RIS size vs computation time
    # ----------------------------------------------

    plt.figure()

    plt.errorbar(
        ris_elements,
        median_computation_times,
        yerr=[
            lower_errors,
            upper_errors
        ],
        marker="o",
        capsize=5
    )

    plt.xlabel("Number of RIS Elements")
    plt.ylabel("Median Computation Time (ms)")
    plt.title("Effect of RIS Size on Computation Time")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "results/ris_size_vs_computation_time.png",
        dpi=300
    )

    plt.show()

def plot_csi_results(csi_results):
    """
    Create and save plots for the imperfect CSI experiment.
    """

    import os
    import matplotlib.pyplot as plt

    os.makedirs("results", exist_ok=True)

    # Separate Perfect CSI from numerical NMSE values
    perfect_result = csi_results[0]

    imperfect_results = [
        result
        for result in csi_results
        if result["nmse_db"] is not None
    ]

    nmse_values = [
        result["nmse_db"]
        for result in imperfect_results
    ]

    snr_improvements = [
        result["snr_improvement_db"]
        for result in imperfect_results
    ]

    achievable_rates = [
        result["rate_with_ris_mbps"]
        for result in imperfect_results
    ]

    # --------------------------------------------------
    # Figure 3: CSI error vs SNR improvement
    # --------------------------------------------------

    plt.figure()

    plt.plot(
        nmse_values,
        snr_improvements,
        marker="o",
        label="Imperfect CSI"
    )

    # Perfect CSI reference
    plt.axhline(
        y=perfect_result["snr_improvement_db"],
        linestyle="--",
        label="Perfect CSI"
    )

    plt.xlabel("CSI Estimation Error, NMSE (dB)")
    plt.ylabel("SNR Improvement (dB)")
    plt.title(
        "Effect of CSI Estimation Error on RIS SNR Gain"
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "results/csi_nmse_vs_snr_improvement.png",
        dpi=300
    )

    # --------------------------------------------------
    # Figure 4: CSI error vs achievable rate
    # --------------------------------------------------

    plt.figure()

    plt.plot(
        nmse_values,
        achievable_rates,
        marker="o",
        label="Imperfect CSI"
    )

    # Perfect CSI reference
    plt.axhline(
        y=perfect_result["rate_with_ris_mbps"],
        linestyle="--",
        label="Perfect CSI"
    )

    plt.xlabel("CSI Estimation Error, NMSE (dB)")
    plt.ylabel("Achievable Rate (Mbps)")
    plt.title(
        "Effect of CSI Estimation Error on Achievable Rate"
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "results/csi_nmse_vs_achievable_rate.png",
        dpi=300
    )

    # Display both figures
    plt.show()

def plot_mobility_update_results(mobility_results):
    """
    Plot RIS performance against update interval
    for different user speeds.
    """

    import os
    import matplotlib.pyplot as plt

    os.makedirs("results", exist_ok=True)

    speeds = sorted(
        set(
            result["speed_mps"]
            for result in mobility_results
        )
    )

    # ----------------------------------------------
    # Figure 5: Update interval vs SNR improvement
    # ----------------------------------------------

    plt.figure()

    for speed in speeds:

        speed_results = [
            result
            for result in mobility_results
            if result["speed_mps"] == speed
        ]

        update_intervals = [
            result["update_interval_ms"]
            for result in speed_results
        ]

        snr_improvements = [
            result["average_snr_improvement_db"]
            for result in speed_results
        ]

        plt.plot(
            update_intervals,
            snr_improvements,
            marker="o",
            label=f"{speed} m/s"
        )

    # Zero-gain reference
    plt.axhline(
        y=0,
        linestyle="--",
        label="No RIS gain"
    )

    plt.xscale("log")

    plt.xlabel("RIS Update Interval (ms)")
    plt.ylabel("Average SNR Improvement (dB)")

    plt.title(
        "Effect of RIS Update Interval Under User Mobility"
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "results/mobility_update_vs_snr_improvement.png",
        dpi=300
    )

    # ----------------------------------------------
    # Figure 6: Update interval vs achievable rate
    # ----------------------------------------------

    plt.figure()

    for speed in speeds:

        speed_results = [
            result
            for result in mobility_results
            if result["speed_mps"] == speed
        ]

        update_intervals = [
            result["update_interval_ms"]
            for result in speed_results
        ]

        rates = [
            result["average_rate_with_ris_mbps"]
            for result in speed_results
        ]

        plt.plot(
            update_intervals,
            rates,
            marker="o",
            label=f"{speed} m/s"
        )

    plt.xscale("log")

    plt.xlabel("RIS Update Interval (ms)")
    plt.ylabel("Average Achievable Rate (Mbps)")

    plt.title(
        "Effect of RIS Update Interval on Achievable Rate"
    )

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "results/mobility_update_vs_achievable_rate.png",
        dpi=300
    )

    plt.show()