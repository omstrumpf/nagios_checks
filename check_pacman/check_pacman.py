#!/usr/bin/python3

import argparse
import subprocess
import sys

DEFAULT_COMMAND = "/usr/bin/pacman"
SUPPORTED_WRAPPERS = {"yay": "/usr/bin/yay", "aura": "/usr/bin/aura"}

# Parse arguments
parser = argparse.ArgumentParser(
    prog="check_pacman", description="Check Pacman (or wrapper) for outdated packages."
)
parser.add_argument("-w", help="warning threshold", type=int, required=True)
parser.add_argument("-c", help="critical threshold", type=int, required=True)
parser.add_argument("-v", help="verbose", action="store_true")
parser.add_argument(
    "--wrapper", help="use a pacman wrapper, such as yay or aura", type=str
)

args = parser.parse_args()

verbose = args.v
warning_threshold = args.w
critical_threshold = args.c

pacman_command = DEFAULT_COMMAND
if args.wrapper is not None:
    if args.wrapper in SUPPORTED_WRAPPERS:
        pacman_command = SUPPORTED_WRAPPERS[args.wrapper]
    else:
        print("PACMAN ERROR: Unsupported wrapper: {args.wrapper}.")
        exit(2)

# Synchronize package databases
sync_result = subprocess.call(
    [pacman_command, "-Sy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
if sync_result != 0:
    print("PACMAN CRITICAL: Failed to sync package databases")
    sys.exit(2)

# Check for outdated packages
stdout, stderr = subprocess.Popen(
    [pacman_command, "-Qu"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
).communicate()

lines = [x for x in stdout.decode("utf-8").split("\n") if x]
num_outdated = len(lines)

outdated_packages = [x.partition(" ")[0] for x in lines]

if num_outdated >= critical_threshold:
    if verbose:
        print(
            f"PACMAN CRITICAL: {num_outdated} packages out of date. Outdated: {outdated_packages}"
        )
    else:
        print(f"PACMAN CRITICAL: {num_outdated} packages out of date.")
    exit(2)
elif num_outdated >= warning_threshold:
    if verbose:
        print(
            f"PACMAN WARNING: {num_outdated} packages out of date. Outdated: {outdated_packages}"
        )
    else:
        print(f"PACMAN WARNING: {num_outdated} packages out of date.")
    exit(1)
else:
    if verbose:
        print(
            f"PACMAN OK: {num_outdated} packages out of date. Outdated: {outdated_packages}"
        )
    else:
        print(f"PACMAN OK: {num_outdated} packages out of date.")
