#!/usr/bin/env python3

import subprocess
from pathlib import Path
import time

# =====================================================
# SETTINGS
# =====================================================

# Folder containing mutant PDB files
MUTANT_DIR = "mutants"

# Delay between simulations (seconds)
# 300 = 5 min
# 0 = no cooldown
COOLDOWN = 3600

# Python MD pipeline script
MD_SCRIPT = "automdver2.py"

# =====================================================
# Find mutant files
# =====================================================

pdb_files = sorted(Path(MUTANT_DIR).glob("*.pdb"))

if len(pdb_files) == 0:

    print("\nNo PDB files found.\n")
    exit()

print("\n===================================================")
print(f"FOUND {len(pdb_files)} MUTANTS")
print("===================================================\n")

# =====================================================
# Sequential execution
# =====================================================

for i, pdb in enumerate(pdb_files, start=1):

    print("\n===================================================")
    print(f"RUNNING MUTANT {i}/{len(pdb_files)}")
    print(f"FILE: {pdb}")
    print("===================================================\n")

    cmd = f'python3 {MD_SCRIPT} "{pdb}"'

    try:

        subprocess.run(
            cmd,
            shell=True,
            check=True
        )

        print("\n===================================================")
        print(f"COMPLETED: {pdb}")
        print("===================================================\n")

    except subprocess.CalledProcessError:

        print("\n===================================================")
        print(f"FAILED: {pdb}")
        print("Moving to next mutant...")
        print("===================================================\n")

    # Cooldown between simulations
    if i < len(pdb_files):

        if COOLDOWN > 0:

            print(f"\nCooling system for {COOLDOWN} seconds...\n")

            try:
                time.sleep(COOLDOWN)

            except KeyboardInterrupt:

                print("\nCooldown interrupted by user.\n")
                exit()

# =====================================================
# Finished
# =====================================================

print("\n===================================================")
print("ALL SIMULATIONS FINISHED")
print("===================================================\n")
