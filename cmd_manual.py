#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

"""EBS Mount - manually mount EBS device (simulates udev add trigger)

Arguments:

    device          EBS device to mount (e.g., /dev/sdf)

Options:

    --format=FS     Format device prior to mount (e.g., --format=ext3)
"""

import os
import sys
import getopt

import ebsmount
import executil
from utils import config, is_mounted

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Syntax: %s [-opts] <device>" % sys.argv[0]
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
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'h', ['format='])
    except getopt.GetoptError, e:
        usage(e)

    filesystem = None
    for opt, val in opts:
        if opt == '-h':
            usage()

        if opt == '--format':
            filesystem = val

    if not len(args) == 1:
        usage()

    devname = args[0]
    if not os.path.exists(devname):
        fatal("%s does not exist" % devname)

    physdevpath = _get_physdevpath(devname)
    if not physdevpath:
        fatal("failed lookup of physdevpath")

    if filesystem:
        if is_mounted(devname):
            fatal("%s is mounted" % devname)

        if not filesystem in config.filesystems.split():
            fatal("%s is not supported in %s" % (filesystem, config.CONF_FILE))

        executil.system("mkfs." + filesystem, "-q", devname)

    mountdir = os.path.join(config.mountdir, os.path.basename(physdevpath))
    ebsmount.ebsmount_add(devname, mountdir)

if __name__=="__main__":
    main()

