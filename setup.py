#!/usr/bin/python3

from distutils.core import setup

setup(
    name="ebsmount",
    version="0.95",
    author="Jeremy Davis",
    author_email="jeremy@turnkeylinux.org",
    url="https://github.com/turnkeylinux/ebsmount",
    packages=["ebsmount_lib"],
    scripts=["cmd_manual.py", "cmd_udev.py"]
)
