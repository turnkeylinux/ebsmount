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

import os
import subprocess
from subprocess import PIPE, STDOUT

from conffile import ConfFile


class EBSMountConf(ConfFile):
    CONF_FILE = '/etc/ebsmount.conf'
    REQUIRED = ['enabled', 'runhooks', 'mountdir', 'mountoptions',
                'filesystems', 'logfile', 'devpaths']


config = EBSMountConf()


def log(devname, s):
    entry = f"{devname}: {s}"
    with open(config.logfile, 'a') as fob:
        fob.write(entry + "\n")
    print(entry)


def mkdir_parents(path, mode=0o777):
    """mkdir 'path' recursively (I.e., equivalent to mkdir -p)"""
    dirs = path.split("/")
    for i in range(2, len(dirs) + 1):
        dir = "/".join(dirs[:i+1])
        if os.path.isdir(dir):
            continue

        os.mkdir(dir, mode)


def is_mounted(path):
    """test if path is mounted"""
    with open("/proc/mounts") as fob:
        mounts = fob.read()
    if mounts.find(path) != -1:
        return True
    return False


def mount(devpath, mountpath, options=''):
    """mount devpath to mountpath with specified options (creates mountpath)"""
    if not os.path.exists(mountpath):
        mkdir_parents(mountpath)

    if options:
        proc = subprocess.run(["systemd-mount", "-o", options, devpath, mountpath],
                              stderr=STDOUT, stdout=PIPE, text=True)
    else:
        proc = subprocess.run(["systemd-mount", devpath, mountpath],
                              stderr=STDOUT, stdout=PIPE, text=True)
    if proc.returncode != 0:
        print(f'An error occurred when mounting:\n{proc.stdout}')
