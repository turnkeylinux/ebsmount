
from os.path import *

import udevdb
from utils import is_mounted, mount

def ebsmount_add(devname, mountdir):
    """ebs device attached"""

    matching_devices = []
    for device in udevdb.query():
        if device.name.startswith(basename(devname)):
            matching_devices.append(device)

    for device in matching_devices:
        devpath = join('/dev', device.name)
        mountpath = join(mountdir, device.env.get('ID_FS_UUID', devpath[-1])[:4])
        mountoptions = "noatime"

        filesystem = device.env.get('ID_FS_TYPE', None)
        if not filesystem:
            print "could not identify filesystem: %s" % devpath
            continue

        if is_mounted(devpath):
            print "already mounted: %s" % devpath
            continue

        mount(devpath, mountpath, mountoptions)
        print "mounted %s %s (%s)" % (devpath, mountpath, mountoptions)

def ebsmount_remove(devname, mountdir):
    """ebs device detached"""
    pass

