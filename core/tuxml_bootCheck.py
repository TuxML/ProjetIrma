#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import time
import re

# Function used to boot up a given kernel
# WARNING : USES qemu-system-x86_64 !
# path is the path to the sources of the kernel
# Returns 0 if the kernel did boot, 1 if it did not and 99 if the check timed out
# Return -2 if the subprocess call failed for whatever reason
def bootTry(path):

	cmd = "qemu-system-x86_64"
	sbStatus = subprocess.call(["mkinitramfs","-o", path + "/arch/x86_64/boot/initrd.img-4.13.3"])
	
	if sbStatus == 0:
		
		procId = subprocess.Popen([cmd, "-kernel", path + "/arch/x86_64/boot/bzImage", "-initrd", path + "/arch/x86_64/boot/initrd.img-4.13.3", "-m", "1G", "-append", "console=ttyS0,38400", "-serial", "file:serial.out"])
	
		rndCounter = 1
		status = -1
	
		time.sleep(5)
		outFile = open("serial.out",mode='r')
		
		while status == -1:
			time.sleep(10)
			print("Reading output file for boot end, attempt", rndCounter)
			fileData = outFile.read()
		
			if re.search("end Kernel panic", fileData):
				print("Kernel panic detected, kernel probably failed to boot !")
				status = 1
			
			if re.search("(initramfs)", fileData):
				print("Shell detected, kernel successfully booted !")
				status = 0
				
			if rndCounter == 61:
				print("More than 60 attempts at reading, possible infinite loop in boot process, interrupting")
				status = 99
				
			rndCounter = rndCounter + 1
				
		procId.terminate() # <-- terminate the process
		outFile.close()
		return status
		
	else:
		return -2

# Testing main program, TODO : Remove once tuxml_bootCheck is integrated into tuxml.py
bootTry("/root/Downloads/linux-4.13.3/")
