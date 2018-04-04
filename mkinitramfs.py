#!/usr/bin/python3

import subprocess
import sys

OUTPUT = sys.__stdout__

try:
	sbStatus = subprocess.call(["mkinitramfs","-o", "../linux-4.13.3/arch/x86_64/boot/initrd.img-4.13.3"])
except FileNotFoundError:
	sbStatus = -1;

print(sbStatus)
