#!/usr/bin/python
"""EBS Mount - triggered by udev on EBS attach and detach

Arguments:

    action          action trigger (add | remove)

Environment variables:

    DEVNAME         (required: e.g., /dev/sdh)
    PHYSDEVPATH     (required: e.g., /devices/xen/vbd-2160)
"""

import os
import sys

import ebsmount
from utils import log, config

def usage(e=None):
    if e:
        print >> sys.stderr, "error: " + str(e)

    print >> sys.stderr, "Syntax: %s <action>" % sys.argv[0]
    print >> sys.stderr, __doc__.strip()
    sys.exit(1)

def fatal(s):
    print >> sys.stderr, "error: " + str(s)
    sys.exit(1)

def main():
    if not len(sys.argv) == 2:
        usage()

    action = sys.argv[1]
    DEVNAME = os.getenv('DEVNAME', None)
    PHYSDEVPATH = os.getenv('PHYSDEVPATH', None)

    if not action in ('add', 'remove'):
        usage('action must be one of: add, remove')

    if not DEVNAME:
        usage('DEVNAME is required')

    if not PHYSDEVPATH:
        usage('PHYSDEVPATH is required')

    if not PHYSDEVPATH.startswith('/devices/xen/vbd-'):
        usage('PHYSDEVPATH is not of the expected structure')

    # log trigger
    log(DEVNAME, "received %s trigger" % action)

    mountdir = os.path.join(config.mountdir, os.path.basename(PHYSDEVPATH))
    func = getattr(ebsmount, 'ebsmount_' + action)
    func(DEVNAME, mountdir)

if __name__=="__main__":
    main()

