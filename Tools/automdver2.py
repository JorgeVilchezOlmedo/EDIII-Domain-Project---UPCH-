#!/usr/bin/env python3

import subprocess
import sys
import os
import shutil
from pathlib import Path

# =========================================================
# Headless / cluster-safe execution
# =========================================================

os.environ["GMX_NO_X11"] = "1"
os.environ["DISPLAY"] = ""

# =========================================================
# USER SETTINGS
# =========================================================

GMX = "gmx_mpi"

# Adjust according to your hardware
THREADS = "4"

# GPU acceleration flags
GPU_FLAGS = "-nb gpu -pme gpu -pin on"

# Uncomment ONLY if supported by your GROMACS version
# GPU_FLAGS = "-nb gpu -bonded gpu -pme gpu -update gpu -pin on"

# Force field and water model selections
# These numbers depend on your GROMACS installation.
#
# Typical examples:
# 1 = amber99sb-ildn
# 1 = tip3p
#
# Run manually once:
# gmx pdb2gmx
# and verify the correct numbers.

FORCEFIELD_SELECTION = "1"
WATER_SELECTION = "1"

# =========================================================
# Helper function
# =========================================================

def run_command(command, description, logfile="pipeline.log"):

    print("\n===================================================")
    print(description)
    print("===================================================")
    print(f"Running:\n{command}\n")

    env = os.environ.copy()

    with open(logfile, "a") as log:

        log.write("\n===================================================\n")
        log.write(description + "\n")
        log.write("===================================================\n")
        log.write(command + "\n\n")

        try:

            process = subprocess.run(
                command,
                shell=True,
                check=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            print(process.stdout)
            log.write(process.stdout)

        except subprocess.CalledProcessError as e:

            print("\nERROR DETECTED\n")
            print(e.stdout)

            log.write("\nERROR DETECTED\n")
            log.write(e.stdout)

            sys.exit(1)
# =========================================================
# Absolute paths
# =========================================================

SCRIPT_DIR = Path(__file__).resolve().parent
MDP_DIR = SCRIPT_DIR / "MDPs"

# =========================================================
# File validation
# =========================================================

def check_required_files():

    required = [
        MDP_DIR / "ions.mdp",
        MDP_DIR / "minim.mdp",
        MDP_DIR / "nvt.mdp",
        MDP_DIR / "npt.mdp",
        MDP_DIR / "md.mdp"
    ]

    for file in required:

        if not file.exists():

            print(f"\nMissing required file:\n{file}")
            sys.exit(1)

# =========================================================
# Main pipeline
# =========================================================
# =========================================================
# Main pipeline
# =========================================================

def main():

    if len(sys.argv) != 2:

        print("\nUsage:")
        print("./md_sim.py protein.pdb\n")
        sys.exit(1)

    pdb_file = sys.argv[1]

    if not pdb_file.endswith(".pdb"):

        print("\nInput file must be a .pdb\n")
        sys.exit(1)

    if not Path(pdb_file).exists():

        print(f"\nFile not found:\n{pdb_file}\n")
        sys.exit(1)

    check_required_files()

    base_name = Path(pdb_file).stem

    # =====================================================
    # Create working directory
    # =====================================================

    workdir = Path(base_name)

    if workdir.exists():

        print(f"\nDirectory already exists:\n{workdir}")
        print("Remove it or rename the input file.\n")
        sys.exit(1)

    workdir.mkdir()

    shutil.copy(pdb_file, workdir)

    os.chdir(workdir)

    pdb_local = Path(pdb_file).name

    print("\n===================================================")
    print("STARTING MOLECULAR DYNAMICS PIPELINE")
    print("===================================================\n")

      # =====================================================
    # STEP 1 — pdb2gmx
    # =====================================================

    cmd1 = (
        f'echo "{FORCEFIELD_SELECTION} {WATER_SELECTION}" | '
        f'{GMX} pdb2gmx '
        f'-f "{pdb_local}" '
        f'-o processed.gro '
        f'-water tip3p '
        f'-ff amber99sb-ildn'
    )

    run_command(
        cmd1,
        "STEP 1 — Generating topology and coordinates"
    )

    # =====================================================
    # STEP 2 — Define box
    # =====================================================

    cmd2 = (
        f'{GMX} editconf '
        f'-f processed.gro '
        f'-o box.gro '
        f'-c '
        f'-d 1.0 '
        f'-bt triclinic'
    )

    run_command(
        cmd2,
        "STEP 2 — Creating triclinic simulation box"
    )

    # =====================================================
    # STEP 3 — Solvation
    # =====================================================

    cmd3 = (
        f'{GMX} solvate '
        f'-cp box.gro '
        f'-cs spc216.gro '
        f'-o solv.gro '
        f'-p topol.top'
    )

    run_command(
        cmd3,
        "STEP 3 — Solvating system with TIP3P-compatible water"
    )

      # =====================================================
    # STEP 4 — Prepare ions
    # =====================================================

    cmd4 = (
        f'{GMX} grompp '
        f'-f "{MDP_DIR}/ions.mdp" '
        f'-c solv.gro '
        f'-p topol.top '
        f'-o ions.tpr '
        f'-maxwarn 1'
    )

    run_command(
        cmd4,
        "STEP 4 — Preparing ion generation"
    )

       # =====================================================
    # STEP 5 — Add ions
    # =====================================================

    cmd5 = (
        f'echo "SOL" | '
        f'{GMX} genion '
        f'-s ions.tpr '
        f'-o ions.gro '
        f'-p topol.top '
        f'-pname NA '
        f'-nname CL '
        f'-neutral'
    )

    run_command(
        cmd5,
        "STEP 5 — Adding counterions"
    )

    # =====================================================
    # STEP 6 — Energy minimization
    # =====================================================

    cmd6 = (
        f'{GMX} grompp '
        f'-f "{MDP_DIR}/minim.mdp" '
        f'-c ions.gro '
        f'-p topol.top '
        f'-o em.tpr'
    )

    run_command(
        cmd6,
        "STEP 6 — Preparing energy minimization"
    )

    cmd7 = (
        f'{GMX} mdrun '
        f'-deffnm em '
        f'-ntomp {THREADS} '
        f'-v'
    )

    run_command(
        cmd7,
        "STEP 7 — Running energy minimization"
    )
    # =====================================================
    # STEP 8 — NVT equilibration
    # =====================================================

    cmd8 = (
    f'{GMX} grompp '
    f'-f "{MDP_DIR}/nvt.mdp" '
    f'-c em.gro '
    f'-r em.gro '
    f'-p topol.top '
    f'-o nvt.tpr'
	)
    run_command(
        cmd8,
        "STEP 8 — Preparing NVT equilibration"
    )

    cmd9 = (
        f'{GMX} mdrun '
        f'-deffnm nvt '
        f'-ntomp {THREADS} '
        f'{GPU_FLAGS} '
        f'-v'
    )

    run_command(
        cmd9,
        "STEP 9 — Running NVT equilibration"
    )

    # =====================================================
    # STEP 10 — NPT equilibration
    # =====================================================

    cmd10 = (
    f'{GMX} grompp '
    f'-f "{MDP_DIR}/npt.mdp" '
    f'-c nvt.gro '
    f'-r nvt.gro '
    f'-t nvt.cpt '
    f'-p topol.top '
    f'-o npt.tpr'
)
    run_command(
        cmd10,
        "STEP 10 — Preparing NPT equilibration"
    )

    cmd11 = (
        f'{GMX} mdrun '
        f'-deffnm npt '
        f'-ntomp {THREADS} '
        f'{GPU_FLAGS} '
        f'-v'
    )

    run_command(
        cmd11,
        "STEP 11 — Running NPT equilibration"
    )

    # =====================================================
    # STEP 12 — Production MD
    # =====================================================

    cmd12 = (
    f'{GMX} grompp '
    f'-f "{MDP_DIR}/md.mdp" '
    f'-c npt.gro '
    f'-t npt.cpt '
    f'-p topol.top '
    f'-o md.tpr'
)

    run_command(
        cmd12,
        "STEP 12 — Preparing production simulation"
    )

 # =====================================================
    # STEP 13 — Production MD
    # =====================================================

    if Path("md.cpt").exists():

        print("\nCheckpoint detected — resuming previous simulation.\n")

        cmd13 = (
            f'{GMX} mdrun '
            f'-deffnm md '
            f'-ntomp {THREADS} '
            f'{GPU_FLAGS} '
            f'-cpi md.cpt '
            f'-append '
            f'-v'
        )

    else:

        print("\nNo checkpoint detected — starting new simulation.\n")

        cmd13 = (
            f'{GMX} mdrun '
            f'-deffnm md '
            f'-ntomp {THREADS} '
            f'{GPU_FLAGS} '
            f'-v'
        )

    run_command(
        cmd13,
        "STEP 13 — Running production molecular dynamics"
    )


    # =====================================================
    # Finished
    # =====================================================

    print("\n===================================================")
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("===================================================\n")

    print("Important output files:\n")

    print("Trajectory:")
    print("  md.xtc\n")

    print("Final structure:")
    print("  md.gro\n")

    print("Checkpoint:")
    print("  md.cpt\n")

    print("Energy:")
    print("  md.edr\n")

    print("Log:")
    print("  md.log\n")

    print("Pipeline log:")
    print("  pipeline.log\n")


# =========================================================

if __name__ == "__main__":
    main()
