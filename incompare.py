#!/usr/bin/python3

import subprocess
import argparse
import os
import re
import MySQLdb
import core.tuxml_settings as tset

# Class kernel to compare two of them
class kernel:

    def __init__(self, size, time, cid):
        self.size = size    # Size of kernel
        self.time = time    # Compilation time
        self.cid = cid      # Cid of the kernel in Database

    def get_size(self):
        return self.size

    def get_time(self):
        return self.time

    def get_cid(self):
        return self.cid

    def pprint(self):
        return "Cid: " + str(self.cid) + "\nCompilation time: " + str(self.time) + "\nSize: " + str(self.size)




# Run docker images to compile the kernel in incremental mode
def create_kernel() -> str:
    subprocess.run("sudo ./MLfood.py 1 1 --dev --no-clean", shell=True)
    return subprocess.check_output("sudo docker ps -lq", shell=True).decode().replace("\n","")


# Retrieves .config file and output.log from the docker container and store it in the folder created for this purpose.
def fetch_files(id:int, dockerid: str, mode:str):
    subprocess.run('sudo docker cp ' + dockerid + ':/TuxML/linux-4.13.3/.config ./compare/' + str(id) + '/' + mode + '.config', shell=True)
    subprocess.run('sudo docker cp ' + dockerid + ':/TuxML/output.log ./compare/'+ str(id) + '/' + mode + '-output.log', shell=True)


# Create a new kernel instance from the physical kernel
def compute_kernel(id:int, mode:str) -> kernel:

    cid = -1
    for line in open('compare/'+ str(id) +'/' + mode + '-output.log'):
        match = re.search('DATABASE CONFIGURATION ID=(\d+)', line)
        if match:
            cid = match.group(1)

    if not cid == -1:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "IrmaDB_prod")
        cursor = socket.cursor()
        query = "SELECT * FROM Compilations WHERE cid = " + cid
        cursor.execute(query)
        entry = cursor.fetchone()

        time = entry[2] # Compilation time column
        size = entry[7] # Size of kernel column

        cursor.close()
        socket.close()

        ker = kernel(size,time,cid)
        return ker

    else:
        print("Failed")
        return -1


# Basic compilation based on .config file from incremental
def execute_config(id:int) -> str:
    # Create a new container
    subprocess.run("sudo docker run -i -d tuxml/tuxmldebian:dev", shell=True)
    # Copy on it the .config file to use
    subprocess.run("sudo docker cp ./compare/" + str(id) + "/incr.config $(sudo docker ps -lq):/TuxML/.config", shell=True)
    # Run the compilation with the .config file from the incremental compilation
    subprocess.run("sudo docker exec -t $(sudo docker ps -lq) /TuxML/runandlog.py --path /TuxML/.config", shell=True)
    # Return the last docker id
    return subprocess.check_output("sudo docker ps -lq", shell=True).decode().replace("\n","")


# Give statistics about kernel in incremental mode and basic mode
def compare(incremental:[kernel], basic:[kernel]) -> str:
    long_basic = len(basic)
    long = len(incremental)
    assert long == long_basic , "The two arrays of kernel are not the same size"

    # Return string with statistics on kernels comparison
    stats = "Number of comparisons:", args.compare_number + "\n"

    # Calculate the ratio of same kernel
    ratio_size = []
    ratio_time = []

    for i in long:
        incr = incremental[i]
        base = basic[i]
        ratio_size[i] = (True if incr.get_size() == base.get_size() else False)
        ratio_time[i] = (True if incr.get_time() == base.get_time() else False)

    sizerat = float(ratio_size.count(True) / len(ratio_size))
    timerat = float(ratio_time.count(True) / len(ratio_time))
    stats += "Size ratio: " + sizerat + ' (' + sizerat*100 + ')\n'
    stats += "Time ratio: " + timerat + ' (' + timerat*100 + ')\n'

    if sizerat == 1:
        stats += "Incremental compilation and basic compilations give a kernel with exactly the same size\n"
        stats += "We can assume that for " + args.compare_number + " compilations, incremental and basic does an equivalent work\n"

    return stats




# main
if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("compare_number",type=int, help="The number of comparaison between a basic compilation and a incremental one.\nThe bigger it is, the better")
    args = parser.parse_args()

    if args.compare_number <= 0:
        print("The number of compare to do must be a non-zero positive integer")
        exit(0)

    incremental = []
    basic = []

    for i in range(args.compare_number):
        os.makedirs("./compare/" + str(i), exist_ok=True)

        dockid = create_kernel() # Create incremental kernel
        fetch_files(i,dockid, "incr") # Fetch .config file
        ker_incr = compute_kernel(i, "incr") # Create a kernel instance corresponding to the physical kernel freshly compiled.
        if ker_incr == -1:
            print("Error while retrieving kernel from database")
            exit(1)

        dock_basic = execute_config(i) # Run a basic compilation with the .config file retrieves from the incremental compilation
        fetch_files(i, dock_basic, "basic") # Fetch .config file
        print("")
        ker_basic = compute_kernel(i, "basic")  # Create a new kernel instance attribuate to the kernel compiled in basic mode
        if ker_basic == -1:
            print("Error while retrieving kernel from database")
            exit(1)

        incremental.append(ker_incr)
        basic.append(ker_basic)

    result = compare(incremental, basic)
    print(result)
