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

"""EBS Mount - manually mount EBS device (simulates udev add trigger)

Arguments:

    device          EBS device to mount (e.g., /dev/sdf, /dev/vda)

Options:

    --format=FS     Format device prior to mount (e.g., --format=ext3)
"""

import re
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

    if not _expected_devpath(devname, config.devpaths.split()):
        fatal("devpath not of expected structure, or failed lookup")

    if filesystem:
        if is_mounted(devname):
            fatal("%s is mounted" % devname)

        if not filesystem in config.filesystems.split():
            fatal("%s is not supported in %s" % (filesystem, config.CONF_FILE))

        executil.system("mkfs." + filesystem, "-q", devname)

    ebsmount.ebsmount_add(devname, config.mountdir)

if __name__=="__main__":
    main()

