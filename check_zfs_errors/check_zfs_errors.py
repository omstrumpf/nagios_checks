#!/usr/bin/python3

import argparse
import re
import subprocess
import sys

ERRORS_REGEX = re.compile(
    r"^\s*(?P<entry>\S+)\s+(?P<state>\S+)\s+(?P<read>\d+)\s+(?P<write>\d+)\s+(?P<checksum>\d+)\s+(?P<slow>\d+)$",
    re.MULTILINE,
)
SCRUB_REGEX = re.compile(
    r"scan:.*repaired (?P<bytes>\S+) .* with (?P<errors>\d+) errors"
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

result = stdout.decode("utf-8")

scrub_match = re.search(SCRUB_REGEX, result)

scrub_warning = None
if not scrub_match:
    print(f"ZFS Errors WARNING ({pool_name}): No recent scrub.")
else:
    if int(scrub_match["errors"]) > 0:
        repaired_errors = scrub_match["errors"]
        repaired_bytes = scrub_match["bytes"]
        scrub_warning = f"ZFS Errors WARNING ({pool_name}): Scrub repaired {repaired_bytes} with {repaired_errors} errors."

matches = re.findall(ERRORS_REGEX, result)

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
    if scrub_warning:
        print(scrub_warning)
    else:
        print(
            f"ZFS Errors OK ({pool_name}): All {num_online} entries online with no errors."
        )
elif num_online != len(matches):
    print(
        f"ZFS Errors CRITICAL ({pool_name}): {len(matches) - num_online} entries not online."
    )
else:
    print(f"ZFS Errors CRITICAL ({pool_name}): {total_all} errors detected.")
