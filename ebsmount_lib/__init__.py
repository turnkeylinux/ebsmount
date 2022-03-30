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
# XXX TODO may need additional imports below (moving from importing *)
from os.path import join, basename, exists
import subprocess
from subprocess import STDOUT, PIPE

import pwd

from .udevdb import query
from .utils import config, log, is_mounted, mount


def ebsmount_add(devname, mountdir):
    """ebs device attached"""

    matching_devices = []
    for device in query():
        if device.name.startswith(basename(devname)):
            matching_devices.append(device)

    for device in matching_devices:
        devpath = join('/dev', device.name)
        mountpath = join(mountdir, device.env.get(
            'ID_FS_UUID', devpath[-1])[:6])
        mountoptions = " ".join(config.mountoptions.split())
        hookspath = join(mountpath, ".ebsmount")

        filesystem = device.env.get('ID_FS_TYPE', None)
        if not filesystem:
            log(devname, f"could not identify filesystem: {devpath}")
            continue

        if filesystem not in config.filesystems.split():
            log(devname,
                f"invalid filesystem: {filesystem}, encountered while"
                f" adding {devpath}")
            continue

        if is_mounted(devpath):
            log(devname, f"already mounted: {devpath}")
            continue

        mount(devpath, mountpath, mountoptions)
        log(devname, f"mounted {devpath} {mountpath} ({mountoptions})")

        if exists(hookspath):
            hooks = os.listdir(hookspath)
            hooks.sort()

            if hooks and not config.runhooks.lower() == "true":
                log(devname, "skipping hooks: RUNHOOKS not set to True")
                continue

            for file in hooks:
                fpath = join(hookspath, file)
                if not os.access(fpath, os.X_OK):
                    log(devname, f"skipping hook: '{file}', not executable")
                    continue

                if (not os.stat(fpath).st_uid == 0 or
                        not os.stat(fpath).st_gid == 0):
                    log(devname,
                        f"skipping hook: '{file}', not owned root:root")
                    continue

                log(devname, f"executing hook: {file}")
                os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir
                os.environ['MOUNTPOINT'] = mountpath
                proc = subprocess.run(['/bin/bash', '--login', '-c', fpath],
                                      stderr=STDOUT, stdout=PIPE, check=True)
                subprocess.run(['tee', '-a', config.logfile],
                               input=proc.stdout)


def ebsmount_remove(devname, mountdir):
    """ebs device detached"""

    mounted = False
    try:
        for d in os.listdir(mountdir):
            path = join(mountdir, d)
            print(f'checking path: {path}')
            if is_mounted(path):
                print(f'path mounted: {path}')
                mounted = True
                continue
            os.rmdir(path)

        if not mounted:
            os.rmdir(mountdir)
    except FileNotFoundError:
        pass
