#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

# =========================================================
# SETTINGS
# =========================================================

GMX = "gmx_mpi"

# =========================================================
# Helper function
# =========================================================

def run(cmd, desc):

    print("\n===================================================")
    print(desc)
    print("===================================================\n")

    print(f"Running:\n{cmd}\n")

    try:

        subprocess.run(
            cmd,
            shell=True,
            check=True
        )

    except subprocess.CalledProcessError:

        print(f"\nERROR during:\n{desc}\n")
        sys.exit(1)

# =========================================================
# Main analysis pipeline
# =========================================================

def main():

    # -----------------------------------------------------
    # Required files
    # -----------------------------------------------------

    required = [
        "md.tpr",
        "md.xtc",
        "md.gro"
    ]

    for f in required:

        if not Path(f).exists():

            print(f"\nMissing required file:\n{f}\n")
            sys.exit(1)

    print("\n===================================================")
    print("STARTING MD ANALYSIS PIPELINE")
    print("===================================================\n")

    # =====================================================
    # STEP 1 — Create index
    # =====================================================

    # Uses default GROMACS C-alpha group (3)
    # and saves index correctly.

    cmd1 = (
        f'printf "3\\nq\\n" | '
        f'{GMX} make_ndx '
        f'-f md.tpr '
        f'-o index.ndx'
    )

    run(cmd1, "STEP 1 — Creating index file")

      # =====================================================
    # STEP 2A — Remove PBC
    # =====================================================

    # Group 1 = Protein

    cmd2a = (
        f'printf "1\\n1\\n" | '
        f'{GMX} trjconv '
        f'-s md.tpr '
        f'-f md.xtc '
        f'-o noPBC.xtc '
        f'-pbc mol '
        f'-center '
        f'-ur compact '
        f'-n index.ndx'
    )

    run(cmd2a, "STEP 2A — Removing periodic boundary conditions")

    # =====================================================
    # STEP 2B — Rotational/translational fitting
    # =====================================================

    # Group 4 = Backbone

    cmd2b = (
        f'printf "4\\n4\\n" | '
        f'{GMX} trjconv '
        f'-s md.tpr '
        f'-f noPBC.xtc '
        f'-o processed.xtc '
        f'-fit rot+trans '
        f'-n index.ndx'
    )

    run(cmd2b, "STEP 2B — Fitting trajectory")
    # =====================================================
    # STEP 3 — RMSD
    # =====================================================

    # 4 = Backbone

    cmd3 = (
        f'printf "4\\n4\\n" | '
        f'{GMX} rms '
        f'-s md.tpr '
        f'-f processed.xtc '
        f'-n index.ndx '
        f'-o rmsd.xvg'
    )

    run(cmd3, "STEP 3 — Calculating RMSD")

    # =====================================================
    # STEP 4 — RMSF
    # =====================================================

    # 3 = C-alpha

    cmd4 = (
        f'printf "3\\n" | '
        f'{GMX} rmsf '
        f'-s md.tpr '
        f'-f processed.xtc '
        f'-n index.ndx '
        f'-o rmsf.xvg '
        f'-res'
    )

    run(cmd4, "STEP 4 — Calculating RMSF")

    # =====================================================
    # STEP 5 — Radius of gyration
    # =====================================================

    # 1 = Protein

    cmd5 = (
        f'printf "1\\n" | '
        f'{GMX} gyrate '
        f'-s md.tpr '
        f'-f processed.xtc '
        f'-n index.ndx '
        f'-o gyrate.xvg'
    )

    run(cmd5, "STEP 5 — Calculating radius of gyration")

    # =====================================================
    # STEP 6 — Covariance matrix / PCA
    # =====================================================

    # 3 = C-alpha

    cmd6 = (
        f'printf "3\\n3\\n" | '
        f'{GMX} covar '
        f'-s md.tpr '
        f'-f processed.xtc '
        f'-n index.ndx '
        f'-o eigenval.xvg '
        f'-v eigenvec.trr '
        f'-xpma covar.xpm'
    )

    run(cmd6, "STEP 6 — Calculating covariance matrix")

    # =====================================================
    # STEP 7 — PCA projection
    # =====================================================

    cmd7 = (
        f'printf "3\\n3\\n" | '
        f'{GMX} anaeig '
        f'-v eigenvec.trr '
        f'-s md.tpr '
        f'-f processed.xtc '
        f'-first 1 '
        f'-last 2 '
        f'-2d 2dproj.xvg'
    )

    run(cmd7, "STEP 7 — Generating PCA projection")

    # =====================================================
    # STEP 8 — PCA components
    # =====================================================

    cmd8 = (
        f'printf "3\\n" | '
        f'{GMX} anaeig '
        f'-v eigenvec.trr '
        f'-s md.tpr '
        f'-comp comp.xvg'
    )

    run(cmd8, "STEP 8 — Calculating PCA components")

    # =====================================================
    # STEP 9 — Extreme conformations
    # =====================================================

    cmd9 = (
        f'printf "3\\n" | '
        f'{GMX} anaeig '
        f'-v eigenvec.trr '
        f'-s md.tpr '
        f'-f processed.xtc '
        f'-extr extreme.pdb '
        f'-first 1 '
        f'-last 1'
    )

    run(cmd9, "STEP 9 — Extracting extreme structures")

    # =====================================================
    # FINISHED
    # =====================================================

    print("\n===================================================")
    print("ANALYSIS COMPLETED SUCCESSFULLY")
    print("===================================================\n")

    print("Generated files:\n")

    outputs = [
        "processed.xtc",
        "rmsd.xvg",
        "rmsf.xvg",
        "gyrate.xvg",
        "eigenval.xvg",
        "eigenvec.trr",
        "covar.xpm",
        "2dproj.xvg",
        "comp.xvg",
        "extreme.pdb"
    ]

    for f in outputs:
        print(f"  - {f}")

# =========================================================

if __name__ == "__main__":
    main()
