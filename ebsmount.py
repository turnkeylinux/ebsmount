
from os.path import *

import udevdb
from executil import system
from utils import config, log, is_mounted, mount

def ebsmount_add(devname, mountdir):
    """ebs device attached"""

    matching_devices = []
    for device in udevdb.query():
        if device.name.startswith(basename(devname)):
            matching_devices.append(device)

    for device in matching_devices:
        devpath = join('/dev', device.name)
        mountpath = join(mountdir, device.env.get('ID_FS_UUID', devpath[-1])[:4])
        mountoptions = ",".join(config.mountoptions.split())
        scriptpath = join(mountpath, ".ebsmount")

        filesystem = device.env.get('ID_FS_TYPE', None)
        if not filesystem:
            log(devname, "could not identify filesystem: %s" % devpath)
            continue

        if not filesystem in config.filesystems.split():
            log(devname, "filesystem (%s) not supported: %s" % (filesystem,devpath))
            continue

        if is_mounted(devpath):
            log(devname, "already mounted: %s" % devpath)
            continue

        mount(devpath, mountpath, mountoptions)
        log(devname, "mounted %s %s (%s)" % (devpath, mountpath, mountoptions))

        if exists(scriptpath):
            cmd = "run-parts --verbose --exit-on-error %s" % scriptpath
            cmd += " 2>&1 | tee -a %s" % config.logfile
            system(cmd)

def ebsmount_remove(devname, mountdir):
    """ebs device detached"""
    pass

