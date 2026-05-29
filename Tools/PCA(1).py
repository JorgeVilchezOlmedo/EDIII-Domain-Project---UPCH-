#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot multiple eigenvalue and explained variance curves from GROMACS.
Looks for files named eigenval1.xvg, eigenval2.xvg, etc.
Validates that the corresponding eigenvecN.trr file exists.
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import os

def load_xvg(path):
    """Load eigenvalues from .xvg file ignoring comments (#,@)."""
    data = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("@"):
                continue
            parts = line.split()
            try:
                val = float(parts[-1])
                data.append(val)
            except ValueError:
                continue
    return np.array(data, dtype=float)

def main():
    # --- Detect eigenval*.xvg files ---
    eigenval_files = sorted(glob.glob("eigenval*.xvg"))
    if not eigenval_files:
        print("No eigenval*.xvg files found")
        return

    print("Files found:", eigenval_files)

    # Fixed labels for the first five files
    fixed_labels = ["WT", "L312P", "L312H", "L312R", "T322A","T322K","T322F","K310T"]

    # --- Eigenvalue curve plot ---
    plt.figure(figsize=(9,6))
    cmap = plt.cm.get_cmap("tab10", len(eigenval_files))

    for idx, f in enumerate(eigenval_files, start=1):
        eigenvalues = load_xvg(f)
        components = np.arange(1, len(eigenvalues) + 1)

        # Validate existence of corresponding eigenvec file
        trr_file = f.replace("eigenval", "eigenvec").replace(".xvg", ".trr")
        if os.path.isfile(trr_file):
            print(f"CHECK: {trr_file} found for {f}")
        else:
            print(f"WARNING: {trr_file} does not exist for {f}")

        # Assign label: first five with fixed names, rest with filename
        if idx <= len(fixed_labels):
            label = fixed_labels[idx-1]
        else:
            label = os.path.splitext(os.path.basename(f))[0]

        plt.plot(components, eigenvalues, marker="o",
                 color=cmap(idx-1), label=label)

    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 15
    plt.tick_params(axis='both', which='major', labelsize=20)
    plt.xlabel("Eigenvectors", fontsize=25, labelpad=10)
    plt.ylabel("Eigenvalues", fontsize=25, labelpad=10)
    #plt.title("Eigenvalues comparison")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

    # --- Explained variance ---
    plt.figure(figsize=(9,6))

    for idx, f in enumerate(eigenval_files, start=1):
        eigenvalues = load_xvg(f)
        components = np.arange(1, len(eigenvalues) + 1)

        total = np.sum(eigenvalues)
        explained = eigenvalues / total
        cumulative = np.cumsum(explained)

        # Fixed label or filename
        if idx <= len(fixed_labels):
            label_var = fixed_labels[idx-1]
        else:
            label_var = os.path.splitext(os.path.basename(f))[0]

        # Explained variance bars
        plt.bar(components + 0.1*idx, explained*100, width=0.1,
                label=f"{label_var} variance")

        # Cumulative line
        plt.plot(components, cumulative*100, marker="o",
                 color=cmap(idx-1), linestyle="--",
                 label=f"{label_var} cumulative")

    plt.xlabel("Principal components")
    plt.ylabel("Percentage (%)")
    plt.title("Explained and cumulative variance per component")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()

