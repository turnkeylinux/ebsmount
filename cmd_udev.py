#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

"""EBS Mount - triggered by udev on EBS attach and detach

Arguments:

    action          action trigger (add | remove)

Environment variables (Amazon EC2):

    DEVNAME         (required: e.g., /dev/sdf)
    PHYSDEVPATH     (required: e.g., /devices/xen/vbd-2160)

Environment variables (Eucalyptus):

    DEVNAME         (required: e.g., /dev/vda)
    DEVPATH         (required: e.g., /devices/virtio-pci/virtio0/block/vda)

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

def _expected_devpath(devpath, devpaths):
    for s in devpaths:
        if devpath.startswith(s):
            return True

    return False

def main():
    if not len(sys.argv) == 2:
        usage()

    if not config.enabled.lower() == "true":
        fatal('ebsmount is not enabled (%s)' % config.CONF_FILE)

    action = sys.argv[1]
    devname = os.getenv('DEVNAME', None)
    devpath = os.getenv('PHYSDEVPATH', os.getenv('DEVPATH', None))

    if not action in ('add', 'remove'):
        usage('action must be one of: add, remove')

    if not devname:
        usage('DEVNAME is required')

    if not devpath:
        usage('PHYSDEVPATH or DEVPATH is required')

    if not _expected_devpath(devpath, config.devpaths.split()):
        usage('PHYSDEVPATH/DEVPATH is not of the expected structure')

    # log trigger
    log(devname, "received %s trigger" % action)

    func = getattr(ebsmount, 'ebsmount_' + action)
    func(devname, config.mountdir)

if __name__=="__main__":
    main()

