#!/usr/bin/python3
# -*- coding: utf-8 -*-

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import subprocess
import time
import re
import tuxml_common as tcom
import tuxml_settings as tset

## @file tuxml_bootCheck.py
# @author CHÉDOTAL Corentin
# @brief File containing the functions used to test compiled kernels
# @copyright Apache License, Version 2.0

## @brief Function used to boot up a given kernel if it can
# @details Uses qemu-system-x86_64 to boot the kernel and checks if a shell opens up
# @returns 0 if the kernel did boot, -1 if it did not and -2 if the check timed out, -3 if the function in itself failed for whatever reason
# @deprecated The use of mkinitramfs is deprecated as it is incompatible with the computing grids
def boot_try():
	tcom.pprint(2, "Launching boot test on kernel")

	try:
		sbStatus = subprocess.call(["mkinitramfs","-o", tset.PATH + "/arch/x86_64/boot/initrd.img-4.13.3"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)
	except Exception:
		sbStatus = -1;

	cmd = "qemu-system-x86_64"
	print(sbStatus)
	if sbStatus == 0:
		procId = subprocess.Popen([cmd, "-kernel", tset.PATH + "/arch/x86_64/boot/bzImage", "-initrd", tset.PATH + "/arch/x86_64/boot/initrd.img-4.13.3", "-m", "1G", "-append", "console=ttyS0,38400", "-serial", "file:serial.out"], stdout=tset.OUTPUT, stderr=tset.OUTPUT)

		rndCounter = 1
		status = 1

		time.sleep(5)
		
		try:
			outFile = open("serial.out",mode='r')
		except OSError:
			tcom.pprint(1, "Unable to open output file, assuming subprocess call failed !")
			return -3

		while status == 1:
			time.sleep(10)
			# tcom.pprint(3, "Reading output file for boot end, attempt".format(rndCounter))
			fileData = outFile.read()

			if re.search("(initramfs)", fileData):
				tcom.pprint(0, "Shell detected, kernel successfully booted")
				status = 0

			if re.search("end Kernel panic", fileData):
				tcom.pprint(1, "Kernel panic detected, kernel probably failed to boot")
				status = -1

			if rndCounter == 11: # default 51
				tcom.pprint(1, "More than 60 attempts at reading, possible infinite loop in boot process, interrupting")
				status = -2

			rndCounter = rndCounter + 1

		procId.terminate() # <-- terminate the process
		outFile.close()
		return status
	else:
		return -3
