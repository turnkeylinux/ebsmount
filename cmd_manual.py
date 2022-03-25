#!/usr/bin/python3
# Copyright (c) 2010-2021 Alon Swartz <alon@turnkeylinux.org>
# Copyright (c) 2022 TurnKey GNU/Linux <admin@turnkeylinux.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""EBS Mount - manually mount EBS device (simulates udev add trigger)"""

import re
import os
import sys
import argparse
import subprocess
from subprocess import PIPE, STDOUT

import ebsmount_lib as ebsmount
from ebsmount_lib.utils import config, is_mounted


def fatal(s):
    print("error: " + str(s), file=sys.stderr)
    sys.exit(1)


def _expected_devpath(devname, devpaths):
    """ugly hack to test expected structure of devpath"""
    raw_output = executil.getoutput('udevadm info -a -n %s' % devname)

    for line in raw_output.splitlines():
        line = line.strip()
        m = re.match("^looking at parent device '(.*)':", line)
        if m:
            devpath = m.group(1)
            for pattern in devpaths:
                if re.search(pattern, devpath):
                    return True

    return False


def main():
    parser = argparse.ArgumentParser(
        prog='ebsmount-manual',
        description=("EBS Mount - manually mount EBS device"
                     " (simulates udev add trigger)")
    )
    parser.add_argument(
        'devname',
        nargs=1,
        help="EBS device to mount (e.g., /dev/xvdf, /dev/vda)"
    )
    parser.add_argument(
        '--format',
        dest="filesystem",
        nargs='?',
        default=None,
        choices=["ext2", "ext3", "ext4"],
        const="ext4",
        help="Format device prior to mount (defaults to ext4 unless specified)"
    )
    args = parser.parse_args()
    if not os.path.exists(args.devname):
        raise argparse.ArgumentTypeError(f"{devname} does not exist")

    if not _expected_devpath(devname, config.devpaths.split()):
        raise argparse.ArgumentTypeError(
                "devpath not of expected structure, or failed lookup")

    if filesystem:
        if is_mounted(devname):
            raise argparse.ArgumentTypeError(f"{devname} is mounted")

        if filesystem not in config.filesystems.split():
            raise argparse.ArgumentTypeError(
                    f"{filesystem} is not supported in {config.CONF_FILE}")

        format_dev = subprocess([f"mkfs.{filesystem}", "-q", devname],
                                stdout=PIPE, stderr=STDOUT, text=True)
        if format_dev.returncode != 0:
            fatal(f"formating {filesystem} failed: {format_dev.stdout}")

    ebsmount.ebsmount_add(devname, config.mountdir)


if __name__ == "__main__":
    main()
