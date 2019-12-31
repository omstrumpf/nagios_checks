#!/usr/bin/python3

import argparse
import re
import subprocess
import sys

ERRORS_REGEX = re.compile(
    r"^\s*(?P<entry>\S+)\s+(?P<state>\S+)\s+(?P<read>\d+)\s+(?P<write>\d+)\s+(?P<checksum>\d+)\s+(?P<slow>\d+)$",
    re.MULTILINE,
)

# Parse arguments
parser = argparse.ArgumentParser(
    prog="check_zfs_errors",
    description="Check ZFS pool for read, write, checksum, and slow access errors.",
)
parser.add_argument("pool", help="pool name", type=str)

args = parser.parse_args()

pool_name = args.pool

stdout, stderr = subprocess.Popen(
    ["zpool", "status", "-psv", pool_name],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
).communicate()

matches = re.findall(ERRORS_REGEX, stdout.decode("utf-8"))

num_online = 0
total_r = 0
total_w = 0
total_c = 0
total_s = 0

for name, status, r, w, c, s in matches:
    if status == "ONLINE":
        num_online += 1
    total_r += int(r)
    total_w += int(w)
    total_c += int(c)
    total_s += int(s)

total_all = total_r + total_w + total_c + total_s

if total_all == 0 and num_online == len(matches):
    # TODO check for errors repaired in scrub, warning if so.
    print(
        f"ZFS Errors OK ({pool_name}): All {num_online} entries online with no errors."
    )
elif num_online != len(matches):
    print(
        f"ZFS Errors Critical ({pool_name}): {len(matches) - num_online} entries not online."
    )
else:
    print(f"ZFS Errors Critical ({pool_name}): {total_all} errors detected.")
