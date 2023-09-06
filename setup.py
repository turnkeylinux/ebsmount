#!/usr/bin/python3

from distutils.core import setup

setup(
    name="ebsmount",
    version="0.97",
    author="Jeremy Davis",
    author_email="jeremy@turnkeylinux.org",
    url="https://github.com/turnkeylinux/ebsmount",
    packages=["ebsmount_lib"],
    scripts=["ebsmount-manual", "ebsmount-udev"]
)
