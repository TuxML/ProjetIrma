#!/usr/bin/python3

import subprocess
import argparse


parser = argparse.ArgumentParser(description="Clean the Logs/ directory, and all docker containers (running or not) if no arguments are precised.")
parser.add_argument("--logs", help='Only clean "Logs/"', action="store_true")
parser.add_argument("--docker", help='Only clean docker containers', action="store_true")
args = parser.parse_args()

if args.logs:
        print("Deleting Logs...")
        # subprocess.run("sudo rm -rf Logs/*", shell=True)
        subprocess.call("sudo rm -rf Logs/*", shell=True)
        print("All logs have been cleaned")
elif args.docker:
        print("Stopping running Docker containers:")
        # subprocess.run("sudo docker stop $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
        subprocess.call("sudo docker stop $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
        print("")
        print("Deleting Docker containers:")
        # subprocess.run("sudo docker rm $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
        subprocess.call("sudo docker rm $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
        print("All docker containers have been cleaned")
else:
    print("Deleting Logs...")
    # subprocess.run("sudo rm -rf Logs/*", shell=True)
    subprocess.call("sudo rm -rf Logs/*", shell=True)
    print("")
    print("Stopping running Docker containers:")
    # subprocess.run("sudo docker stop $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
    subprocess.call("sudo docker stop $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
    print("")
    print("Deleting Docker containers:")
    # subprocess.run("sudo docker rm $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
    subprocess.call("sudo docker rm $(sudo docker ps -aq)", shell=True, stderr=subprocess.DEVNULL)
    print("All docker containers and Logs have been cleaned")
