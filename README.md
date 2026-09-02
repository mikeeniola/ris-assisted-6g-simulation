# RIS-Assisted 6G Wireless Communication Simulation

This repository contains the Python simulation framework developed for an MSc dissertation investigating the performance, scalability and practical limitations of Reconfigurable Intelligent Surfaces (RIS) for prospective 6G wireless communication systems.

## Research Overview

The simulation investigates how RIS-assisted wireless communication is affected by:

1. RIS array size
2. Computational scalability
3. Imperfect Channel State Information (CSI)
4. User mobility
5. RIS reconfiguration interval

The principal performance metrics include Signal-to-Noise Ratio (SNR), achievable data rate and computational execution time.

## Simulation Configuration

The baseline simulation uses:

- Carrier frequency: 30 GHz
- Transmit power: 35 dBm
- Bandwidth: 100 MHz
- Thermal noise density: -174 dBm/Hz
- Receiver noise figure: 9 dB
- Base station position: [0, 0, 10] m
- RIS centre position: [50, 10, 5] m
- Initial user position: [100, 0, 1.5] m

A fixed NumPy random seed of 42 is used to support reproducibility.

## Experiments

### Experiment 1 – RIS Size and Computational Scalability

The RIS element count is varied across:

- 16 elements
- 64 elements
- 256 elements
- 1024 elements

The experiment evaluates SNR, achievable rate and computation time. Timing measurements are repeated 100 times and summarised using the median and interquartile range.

### Experiment 2 – Imperfect CSI

RIS performance is evaluated under:

- Perfect CSI
- -30 dB NMSE
- -20 dB NMSE
- -10 dB NMSE
- 0 dB NMSE

The experiment uses 1,000 trials for each CSI condition and evaluates the resulting SNR and achievable rate.

### Experiment 3 – User Mobility

User speeds of 0, 1, 5 and 15 m/s are investigated using a 1024-element RIS.

The experiment evaluates the effect of user movement on average SNR and achievable rate when the RIS configuration becomes outdated.

### Experiment 3B – Mobility and RIS Reconfiguration

RIS update intervals of 1, 5, 10, 50 and 100 ms are evaluated for user speeds of 1, 5 and 15 m/s.

This experiment investigates how frequently the RIS must be reconfigured to maintain useful performance under mobility.

## Repository Structure

The source code is located in the `RIS_6G_Dissertation` directory.

- `channel_model.py` – wireless channel and path-loss modelling
- `ris_model.py` – RIS geometry, phase configuration and effective channel calculation
- `experiments.py` – implementation of the simulation experiments
- `plots.py` – generation of experimental figures
- `main.py` – main script used to configure and execute the experiments

## Requirements

The simulation is implemented in Python.

The main numerical dependency is:

- NumPy

Plot generation also requires:

- Matplotlib

Install the required packages using:

    pip install numpy matplotlib

## Running the Simulation

Download or clone the repository and navigate to the source-code directory:

    cd RIS_6G_Dissertation

Run:

    python main.py

The script executes the baseline simulation and the experimental scenarios and generates the associated results and plots.

## Reproducibility

A fixed NumPy random seed is used for reproducibility. The imperfect-CSI experiment uses repeated trials, while the computational scalability analysis uses repeated execution-time measurements.

Results may show small differences in execution time between computers because timing measurements depend on hardware, operating system and background processes.

## Academic Purpose

This repository accompanies an MSc dissertation investigating RIS-assisted wireless communication for prospective 6G networks. The code is provided to support transparency and reproducibility of the simulation methodology and experimental results.
