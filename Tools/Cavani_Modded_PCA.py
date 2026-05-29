#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# =====================================================
# USER PARAMETERS
# =====================================================

N_COMPONENTS = 10   # show only first 10 eigenvectors

# =====================================================
# FUNCTIONS
# =====================================================

def load_xvg(path):

    data = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:

        for line in f:

            line = line.strip()

            if (
                not line
                or line.startswith("#")
                or line.startswith("@")
            ):
                continue

            parts = line.split()

            try:
                value = float(parts[-1])
                data.append(value)

            except ValueError:
                continue

    return np.array(data, dtype=float)


def extract_label(filename):

    base = os.path.basename(filename)

    label = (
        base
        .replace("_eigenval.xvg", "")
        .replace(".xvg", "")
    )

    return label


# =====================================================
# MAIN
# =====================================================

def main():

    eigenval_files = sorted(
        glob.glob("*eigenval*.xvg")
    )

    if not eigenval_files:
        print("No eigenvalue files found.")
        return

    print("\nDetected files:")
    for f in eigenval_files:
        print(" ", f)

    # -------------------------------------------------
    # Plot settings
    # -------------------------------------------------

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 15

    cmap = plt.colormaps["tab10"]

    # =================================================
    # EIGENVALUE PLOT
    # =================================================

    fig1, ax1 = plt.subplots(figsize=(9, 6))

    for idx, f in enumerate(eigenval_files):

        eigenvalues = load_xvg(f)

        if len(eigenvalues) == 0:
            continue

        # ---------------------------------------------
        # KEEP ONLY FIRST 10 PCs
        # ---------------------------------------------

        eigenvalues = eigenvalues[:N_COMPONENTS]

        components = np.arange(
            1,
            len(eigenvalues) + 1
        )

        label = extract_label(f)

        # ---------------------------------------------
        # Check TRR file
        # ---------------------------------------------

        trr_file = f.replace(
            "eigenval.xvg",
            "eigenvec.trr"
        )

        if os.path.isfile(trr_file):
            print(f"OK: {trr_file}")

        else:
            print(f"WARNING: Missing {trr_file}")

        # ---------------------------------------------
        # Plot
        # ---------------------------------------------

        ax1.plot(
            components,
            eigenvalues,
            marker="o",
            linewidth=2,
            label=label,
            color=cmap(idx % 10)
        )

    ax1.set_xlabel(
        "Principal Components",
        fontsize=22
    )

    ax1.set_ylabel(
        "Eigenvalues",
        fontsize=22
    )

    ax1.set_xticks(range(1, N_COMPONENTS + 1))

    ax1.grid(True, alpha=0.3)

    ax1.legend()

    fig1.tight_layout()

    # =================================================
    # EXPLAINED VARIANCE
    # =================================================

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    for idx, f in enumerate(eigenval_files):

        eigenvalues = load_xvg(f)

        if len(eigenvalues) == 0:
            continue

        # ---------------------------------------------
        # KEEP ONLY FIRST 10 PCs
        # ---------------------------------------------

        eigenvalues = eigenvalues[:N_COMPONENTS]

        components = np.arange(
            1,
            len(eigenvalues) + 1
        )

        label = extract_label(f)

        # ---------------------------------------------
        # Variance calculations
        # ---------------------------------------------

        total = np.sum(eigenvalues)

        explained = eigenvalues / total

        cumulative = np.cumsum(explained)

        # ---------------------------------------------
        # Bar plot
        # ---------------------------------------------

        offset = idx * 0.12

        ax2.bar(
            components + offset,
            explained * 100,
            width=0.12,
            alpha=0.7,
            label=f"{label} variance"
        )

        # ---------------------------------------------
        # Cumulative variance
        # ---------------------------------------------

        ax2.plot(
            components,
            cumulative * 100,
            marker="o",
            linestyle="--",
            linewidth=2,
            color=cmap(idx % 10),
            label=f"{label} cumulative"
        )

    ax2.set_xlabel(
        "Principal Components",
        fontsize=22
    )

    ax2.set_ylabel(
        "Explained Variance (%)",
        fontsize=22
    )

    ax2.set_xticks(range(1, N_COMPONENTS + 1))

    ax2.grid(True, alpha=0.3)

    ax2.legend(
        fontsize=10,
        ncol=2
    )

    fig2.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()
