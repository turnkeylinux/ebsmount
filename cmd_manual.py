#!/usr/bin/python
"""EBS Mount - manually mount EBS device (simulates udev add trigger)

Arguments:

    device          EBS device to mount (e.g., /dev/sdh)
"""

import os
import sys

import ebsmount
import executil
from utils import config

def usage():
    print >> sys.stderr, "Syntax: %s <device>" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()
    sys.exit(1)

def fatal(s):
    print >> sys.stderr, "error: " + str(s)
    sys.exit(1)

def _get_physdevpath(devname):
    """ugly hack to get the physical device path of first parent"""
    raw_output = executil.getoutput('udevadm info -a -n %s' % devname)

    for line in raw_output.splitlines():
        line = line.strip()
        if line.startswith("looking at parent device '/devices/xen/vbd-"):
            return line.split()[-1].strip(":").strip("'")

    return None

def main():
    if not len(sys.argv) == 2:
        usage()

    devname = sys.argv[1]
    physdevpath = _get_physdevpath(devname)

    if not physdevpath:
        fatal("failed lookup of physdevpath")

    mountdir = os.path.join(config.mountdir, os.path.basename(physdevpath))
    ebsmount.ebsmount_add(devname, mountdir)

if __name__=="__main__":
    main()

