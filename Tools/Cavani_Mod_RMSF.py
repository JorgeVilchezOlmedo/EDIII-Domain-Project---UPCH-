#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# =========================================================
# Load RMSF
# =========================================================

def load_rmsf(path):
    """
    Load RMSF data from XVG file.
    Ignores GROMACS headers.
    """

    x = []
    y = []

    with open(path, 'r') as f:

        for line in f:

            if line.startswith(('#', '@')):
                continue

            parts = line.strip().split()

            if len(parts) >= 2:

                x.append(int(float(parts[0])))

                # Convert nm -> Å
                y.append(float(parts[1]) * 10.0)

    return np.array(x), np.array(y)


# =========================================================
# Extract labels automatically
# =========================================================

def extract_label(filepath):

    filename = os.path.basename(filepath)

    filename = os.path.splitext(filename)[0]

    filename = filename.replace("_rmsf", "")
    filename = filename.replace("_RMSF", "")

    return filename


# =========================================================
# Automatically detect RMSF files
# =========================================================

files = sorted(glob.glob("*_rmsf.xvg"))

# Put WT first
if "WT_rmsf.xvg" in files:
    files.remove("WT_rmsf.xvg")
    files.insert(0, "WT_rmsf.xvg")

if len(files) == 0:

    print("No *_rmsf.xvg files found.")
    exit()


print("\nDetected RMSF files:\n")

for f in files:
    print(f"  - {f}")

print()


# =========================================================
# Colors
# =========================================================

colors = [
    (31/255, 119/255, 180/255),   # Blue
    (214/255, 39/255, 40/255),    # Red
    (44/255, 160/255, 44/255),    # Green
    (148/255, 103/255, 189/255),  # Purple
    (255/255, 127/255, 14/255),   # Orange
    (23/255, 190/255, 207/255),   # Cyan
    (140/255, 86/255, 75/255),    # Brown
    (227/255, 119/255, 194/255),  # Pink
    (127/255, 127/255, 127/255),  # Gray
    (188/255, 189/255, 34/255)    # Yellow
]


# =========================================================
# Plot
# =========================================================

plt.rcParams['font.family'] = 'serif'

plt.figure(
    figsize=(12, 7)
)

for i, file in enumerate(files):

    print(f"Reading: {file}")

    x, y = load_rmsf(file)

    label = extract_label(file)

    color = colors[i % len(colors)]

    plt.plot(
        x,
        y,
        label=label,
        color=color,
        linewidth=2
    )

    # Print statistics
    print(
        f"{label:10s} "
        f"Mean RMSF = {np.mean(y):.2f} Å   "
        f"Max RMSF = {np.max(y):.2f} Å"
    )


# =========================================================
# Formatting
# =========================================================

plt.xlabel(
    "Residue",
    fontsize=20,
    labelpad=10
)

plt.ylabel(
    "RMSF [Å]",
    fontsize=20,
    labelpad=10
)

plt.tick_params(
    axis='both',
    which='major',
    labelsize=15
)

plt.grid(
    True,
    linestyle='--',
    alpha=0.4
)

plt.legend(
    fontsize=11,
    frameon=True
)

plt.tight_layout()


# =========================================================
# Save figure
# =========================================================

plt.savefig(
    "RMSF_Comparison.png",
    dpi=600,
    bbox_inches='tight'
)

plt.savefig(
    "RMSF_Comparison.pdf",
    bbox_inches='tight'
)

print("\nSaved:")
print("  - RMSF_Comparison.png")
print("  - RMSF_Comparison.pdf\n")

plt.show()
