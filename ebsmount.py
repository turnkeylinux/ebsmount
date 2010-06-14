# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
from os.path import *

import pwd

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
        mountpath = join(mountdir, device.env.get('ID_FS_UUID', devpath[-1])[:6])
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
            os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir
            cmd = "/bin/bash --login -c 'export PATH; run-parts --verbose %s'" % scriptpath
            cmd += " 2>&1 | tee -a %s" % config.logfile
            system(cmd)

def ebsmount_remove(devname, mountdir):
    """ebs device detached"""

    mounted = False
    for d in os.listdir(mountdir):
        path = join(mountdir, d)
        if is_mounted(path):
            mounted = True
            continue

        os.rmdir(path)

    if not mounted:
        os.rmdir(mountdir)

