#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from scipy.stats import gaussian_kde

def smooth_gaussian(data, degree=35):
    """Gaussian-like smoothing for RMSD curves."""
    window = degree * 2 - 1

    weight = np.ones(window)
    weight_gauss = [
        1 / np.exp((4 * ((i - degree + 1) / float(window)) ** 2))
        for i in range(window)
    ]

    weight *= np.array(weight_gauss)

    smoothed = [
        np.sum(np.array(data[i:i + window]) * weight) / np.sum(weight)
        for i in range(len(data) - window)
    ]

    return np.array(smoothed)


def read_xvg(filepath):
    """Read XVG file ignoring GROMACS headers."""
    data = []

    with open(filepath, "r") as f:
        for line in f:
            if not line.startswith(("@", "#")):
                parts = line.strip().split()

                if len(parts) >= 2:
                    data.append(parts)

    return np.array(data)


def get_column(data, col):
    """Extract column as float array."""
    return np.array([float(row[col]) for row in data])


def extract_label(filepath):
    """
    Automatically generate labels from filenames.

    Examples:
        WT_RMSD.xvg       -> WT
        L312R_RMSD.xvg    -> L312R
        Alpha_RMSD.xvg    -> Alpha
    """

    filename = os.path.basename(filepath)

    # Remove extension
    filename = os.path.splitext(filename)[0]

    # Remove common suffixes
    filename = filename.replace("_RMSD", "")
    filename = filename.replace("RMSD_", "")
    filename = filename.replace("rmsd_", "")
    filename = filename.replace("_rmsd", "")

    return filename


if len(sys.argv) < 2:
    print("Usage:")
    print("./plot_rmsd.py *.xvg")
    sys.exit(1)


files = sys.argv[1:]

colors = [
    (31/255, 119/255, 180/255),   # Blue
    (214/255, 39/255, 40/255),   # Red
    (148/255, 103/255, 189/255), # Purple
    (140/255, 86/255, 75/255),   # Brown
    (23/255, 190/255, 207/255),  # Cyan
    (44/255, 160/255, 44/255),   # Green
    (255/255, 127/255, 14/255),  # Orange
    (227/255, 119/255, 194/255), # Pink
    (127/255, 127/255, 127/255), # Gray
    (188/255, 189/255, 34/255)   # Yellow
]

plt.rcParams['font.family'] = 'serif'

fig = plt.figure(figsize=(10, 6), constrained_layout=True)

gs = fig.add_gridspec(1, 2, width_ratios=[4, 1])

ax_main = fig.add_subplot(gs[0])
ax_hist = fig.add_subplot(gs[1], sharey=ax_main)


for i, file in enumerate(files):

    if not os.path.isfile(file):
        print(f"File not found: {file}")
        continue

    print(f"Reading: {file}")

    data = read_xvg(file)

    time_ps = get_column(data, 0)
    time_ns = time_ps / 1000.0

    rmsd_nm = get_column(data, 1)
    rmsd_angstrom = rmsd_nm * 10.0

    color = colors[i % len(colors)]

    # Automatic label from filename
    label = extract_label(file)

    # Raw trajectory
    ax_main.plot(
        time_ns,
        rmsd_angstrom,
        color=color,
        alpha=0.25,
        linewidth=1,
        label=label
    )

    # Smoothed curve
    degree = 120

    if len(rmsd_angstrom) > degree * 2:

        rmsd_smooth = smooth_gaussian(rmsd_angstrom, degree)

        time_smooth = time_ns[degree:(-1)*(degree-1)]

        ax_main.plot(
            time_smooth,
            rmsd_smooth,
            color=color,
            linewidth=2
        )

    # Distribution after equilibration (20 ns)
    mask_20ns = time_ns >= 20.0

    rmsd_post20 = rmsd_angstrom[mask_20ns]

    if len(rmsd_post20) > 5:

        kde = gaussian_kde(rmsd_post20)

        rmsd_range = np.linspace(
            min(rmsd_post20),
            max(rmsd_post20),
            500
        )

        density = kde(rmsd_range)

        ax_hist.plot(
            density,
            rmsd_range,
            color=color,
            linewidth=2
        )


# ===== Formatting =====

ax_main.set_xlabel("Time [ns]", fontsize=18)
ax_main.set_ylabel("RMSD [Å]", fontsize=18)

ax_main.tick_params(axis='both', labelsize=14)

ax_main.grid(True, alpha=0.3)

ax_hist.set_xlim(left=0)
ax_hist.tick_params(labelleft=False)

ax_main.legend(
    loc="lower right",
    fontsize=11,
    frameon=True
)

plt.show()
