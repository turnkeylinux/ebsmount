# Copyright (c) 2010 Alon Swartz <alon@turnkeylinux.org> - all rights reserved

import os
import executil
from conffile import ConfFile

class EBSMountConf(ConfFile):
    CONF_FILE = os.getenv('EBSMOUNT_CONF', '/etc/ebsmount.conf')
    REQUIRED = ['enabled', 'mountdir', 'mountoptions', 'filesystems', 'logfile', 'devpaths']

config = EBSMountConf()


def log(devname, s):
    entry = "%s: %s" % (devname, s)
    file(config.logfile, 'a').write(entry + "\n")
    print entry

def mkdir_parents(path, mode=0777):
    """mkdir 'path' recursively (I.e., equivalent to mkdir -p)"""
    dirs = path.split("/")
    for i in range(2, len(dirs) + 1):
        dir = "/".join(dirs[:i+1])
        if os.path.isdir(dir):
            continue

        os.mkdir(dir, mode)

def is_mounted(path):
    """test if path is mounted"""
    mounts = file("/proc/mounts").read()
    if mounts.find(path) != -1:
        return True
    return False

def mount(devpath, mountpath, options=None):
    """mount devpath to mountpath with specified options (creates mountpath)"""
    if not os.path.exists(mountpath):
        mkdir_parents(mountpath)

    if options:
        executil.system("mount", "-o", options, devpath, mountpath)
    else:
        executil.system("mount", devpath, mountpath)

