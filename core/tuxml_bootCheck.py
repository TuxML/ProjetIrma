#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import time
import re
import tuxml_common as tcom

# Function used to boot up a given kernel
# WARNING : USES qemu-system-x86_64 !
# path is the path to the sources of the kernel
# Returns 0 if the kernel did boot, -1 if it did not and -2 if the check timed out
# Return -3 if the subprocess call failed for whatever reason
def bootTry(path):
	tcom.pprint(2, "Launching boot test on kernel")

	cmd = "qemu-system-x86_64"
	sbStatus = subprocess.call(["mkinitramfs","-o", path + "/arch/x86_64/boot/initrd.img-4.13.3"])

	if sbStatus == 0:

		procId = subprocess.Popen([cmd, "-kernel", path + "/arch/x86_64/boot/bzImage", "-initrd", path + "/arch/x86_64/boot/initrd.img-4.13.3", "-m", "1G", "-append", "console=ttyS0,38400", "-serial", "file:serial.out"])

		rndCounter = 1
		status = 1

		time.sleep(5)
		outFile = open("serial.out",mode='r')

		while status == 1:
			time.sleep(10)
			tcom.pprint(3, "Reading output file for boot end, attempt", rndCounter)
			fileData = outFile.read()

			if re.search("(initramfs)", fileData):
				tcom.pprint(0, "Shell detected, kernel successfully booted")
				status = 0

			if re.search("end Kernel panic", fileData):
				tcom.pprint(1, "Kernel panic detected, kernel probably failed to boot")
				status = -1

			if rndCounter == 61:
				tcom.pprint(1, "More than 60 attempts at reading, possible infinite loop in boot process, interrupting")
				status = -2

			rndCounter = rndCounter + 1

		procId.terminate() # <-- terminate the process
		outFile.close()
		return status

	else:
		return -3
