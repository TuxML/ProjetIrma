#!/usr/bin/python3

import subprocess
import argparse


parser = argparse.ArgumentParser()
args = parser.parse_args()

print("Deleting Logs...")
subprocess.run("sudo rm -rf Logs/*", shell=True)
print("")
print("Stopping running Docker containers:")
subprocess.run("sudo docker stop $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
print("")
print("Deleting Docker containers:")
subprocess.run("sudo docker rm $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
