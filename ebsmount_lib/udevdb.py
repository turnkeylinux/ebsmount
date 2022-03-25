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

import subprocess
from subprocess import PIPE, STDOUT


class Device:
    """class to hold device information enumerated from udev database"""
    def __init__(self, s, volinfo=True):
        self.path = ''
        self.name = ''
        self.symlinks = []
        self.env = {}

        self._parse_raw_data(s)
        if volinfo:
            self._get_volinfo()

    def _parse_raw_data(self, s):
        for entry in s.splitlines():
            type, value = entry.split(':', 1)
            type = type.strip()
            value = value.strip()

            if type == "P":
                self.path = value
                continue

            if type == "N":
                self.name = value
                continue

            if type == "S":
                self.symlinks.append(value)
                continue

            if type == "E":
                name, val = value.split("=", 1)
                self.env[name] = val.lstrip("=")

    def _get_volinfo(self):
        if 'DEVTYPE' in self.env and self.env['DEVTYPE'] == 'disk':
            proc = subprocess(["vol_id", f"/dev/{self.name}"],
                              capture_output=True, text=True)
            if proc.returncode != 0:
                return
            volume_info = proc.stdout

            for value in volume_info.splitlines():
                name, val = value.split("=")
                if name in self.env:
                    continue

                if not val:
                    continue

                self.env[name] = val


def query(device=None, volinfo=True):
    """query udev database and return device(s) information
       if no device is specified, all devices will be returned
       optionally query volume info (vol_id) on disk devices
    """
    if device:
        cmd = ["udevadm", "info", "--query", "all", "--name", device]
    else:
        cmd = ["udevadm", "info", "--export-db"]

    devices = []
    output = subprocess(cmd, stdout=PIPE, stderr=STDOUT, test=True).stdout
    for s in output.split('\n\n'):
        devices.append(Device(s, volinfo))

    return devices


def _disk_devices():
    """debug/test method to print disk devices"""
    devices = query()
    for dev in devices:
        if 'DEVTYPE' in dev.env and dev.env['DEVTYPE'] == 'disk':
            print('/dev/' + dev.name)

            attrs = list(dev.env.keys())
            attrs.sort()
            column_len = max([len(attr) + 1 for attr in attrs])
            for attr in attrs:
                name = attr + ":"
                print(f"  {name.ljust(column_len)} {dev.env[attr]}")
            print()
