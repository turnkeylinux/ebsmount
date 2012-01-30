#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org>
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

import re
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
    for pattern in devpaths:
        if re.search(pattern, devpath):
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

