#!/usr/bin/python
# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

from executil import ExecError, getoutput

class Device:
    """class to hold device information enumerated from udev database"""
    def __init__(self, s, volinfo=True):
        self.path = None
        self.name = None
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
                name, val = value.split("=")
                self.env[name] = val

    def _get_volinfo(self):
        if self.env.has_key('DEVTYPE') and self.env['DEVTYPE'] == 'disk':
            try:
                volume_info = getoutput('vol_id /dev/%s' % self.name)
            except ExecError:
                return

            for value in volume_info.splitlines():
                name, val = value.split("=")
                if self.env.has_key(name):
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
        cmd = "udevadm info --query all --name %s" % device
    else:
        cmd = "udevadm info --export-db"

    devices = []
    for s in getoutput(cmd).split('\n\n'):
        devices.append(Device(s, volinfo))

    return devices
    
    
def _disk_devices():
    """debug/test method to print disk devices"""
    devices = query()
    for dev in devices:
        if dev.env.has_key('DEVTYPE') and dev.env['DEVTYPE'] == 'disk':
            print '/dev/' + dev.name

            attrs = dev.env.keys()
            attrs.sort()
            column_len = max([ len(attr) + 1 for attr in attrs ])
            for attr in attrs:
                name = attr + ":"
                print "  %s %s" % (name.ljust(column_len), dev.env[attr])
            print

def main():
   _disk_devices()    #used in debugging/testing

if __name__ == '__main__':
    main()

