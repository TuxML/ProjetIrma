#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import time
import re

# Function used to boot up a given kernel using a given debian image 
# WARNING : USES qemu-system-x86_64 !
# image is the location/name of the host image for the kernel (in .qcow2)
# kernel is the location/name of the kernel to be tested (in bzImage)
# Returns 0 if the kernel did boot, 1 if it did not and 99 if the check timed out
def bootTry(image, kernel):

	cmd = "qemu-system-x86_64"
	procId = subprocess.Popen([cmd, image,"-kernel", kernel, "-append", "console=ttyS0,38400", "-serial", "file:serial.out"])
	
	rndCounter = 1
	status = -1
	
	time.sleep(5)
	outFile = open("serial.out",mode='r')
	
	while status < 0:
		time.sleep(10)
		print("Reading output file for boot end, attempt", rndCounter)
		fileData = outFile.read()
	
		if re.search("end Kernel panic", fileData):
			print("Kernel panic detected, kernel probably failed to boot !")
			status = 1
		
		if re.search("login:", fileData):
			print("Login screen detected, kernel successfully booted")
			status = 0
			
		if rndCounter == 201:
			print("More than 200 attempts at reading, possible infinite loop, interrupting")
			status = 99
			
		rndCounter = rndCounter + 1
			
	procId.terminate() # <-- terminate the process
	outFile.close()
	return status

# Testing main program, TODO : Remove once tuxml_bootCheck is integrated into tuxml.py
bootTry("debian_wheezy_amd64_standard.qcow2", "/root/Downloads/linux-4.13.3/arch/x86_64/boot/bzImage")
