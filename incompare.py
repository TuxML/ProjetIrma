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


# Retrieves .config file, output.log and the compiled kernel from the docker container and store it in the folder created for this purpose.
def fetch_files(id:int, dockerid: str, mode:str):
    subprocess.run('sudo docker cp ' + dockerid + ':/TuxML/linux-4.13.3/.config ./compare/' + str(id) + '/' + mode + '.config', shell=True)
    subprocess.run('sudo docker cp ' + dockerid + ':/TuxML/output.log ./compare/'+ str(id) + '/' + mode + '-output.log', shell=True)
    subprocess.run('sudo docker cp ' + dockerid + ':/TuxML/linux-4.13.3/vmlinux ./compare/'+ str(id) + '/' + mode + '-vmlinux', shell=True)


# Create a new kernel instance from the physical kernel
def compute_kernel(id:int, mode:str) -> kernel:

    cid = -1

    # size = subprocess.check_output("wc -c compare/" + str(id) + "/" + mode + "-vmlinux", shell=True).decode().split()[0]
    # time = "0"
    #
    # return kernel(size, time, "000")

    for line in open('compare/'+ str(id) +'/' + mode + '-output.log'):

        if mode=="incr":
            match = re.search('INCREMENTAL CONFIGURATION ID #0=(\d+)', line)
        else:
            match = re.search('DATABASE CONFIGURATION ID=(\d+)', line)

        if match:
            cid = match.group(1)

    if not cid == -1:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "IrmaDB_prod")
        cursor = socket.cursor()
        print("\nCID Used:", cid)
        query = "SELECT * FROM Compilations WHERE cid = " + cid
        cursor.execute(query)
        entry = cursor.fetchone()

        time = entry[2] # Compilation time column
        size = entry[7] # Size of kernel column

        cursor.close()
        socket.close()

        return kernel(size,time,cid)

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
    out = subprocess.check_output("sudo docker ps -lq", shell=True).decode().replace("\n","")
    return out


# Give statistics about kernel in incremental mode and basic mode
def compare(incremental:[kernel], basic:[kernel]) -> str:
    long_basic = len(basic)
    long = len(incremental)
    assert long == long_basic , "The two arrays of kernel are not the same size"

    # Return string with statistics on kernels comparison
    stats = "Number of comparisons: " + str(args.compare_number) + "\n"

    # Calculate the ratio of same kernel
    ratio_size = [0] * long # Creating arrays the size of one of the arrays of kernel to compare
    ratio_time = [0] * long

    for i in range(long):
        incr = incremental[i]
        base = basic[i]
        ratio_size[i] = (True if incr.get_size() == base.get_size() else False)
        ratio_time[i] = (True if incr.get_time() == base.get_time() else False)
        print("incr_size:", incr.get_size(), " basic_size:", base.get_size())
        print("incr_time:", incr.get_time(), " basic_time:", base.get_time())

    sizerat = float(ratio_size.count(True) / len(ratio_size))
    timerat = float(ratio_time.count(True) / len(ratio_time))
    stats += "Size ratio: " + str(sizerat) + ' (' + str(sizerat*100) + '%' + ' similar)\n'
    stats += "Time ratio: " + str(timerat) + ' (' + str(timerat*100) + '%' + ' similar)\n'

    if sizerat >= 0.98 and sizerat <= 1.02:
        stats += "\n"
        stats += "Incremental compilation and basic compilations give a kernel with the same size\n"
        stats += "We can assume that for " + str(args.compare_number) + " compilations, incremental and basic does an equivalent work\n"

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

        print("Comparison number",i)

        os.makedirs("./compare/" + str(i), exist_ok=True)

        dockid = create_kernel() # Create incremental kernel
        fetch_files(i,dockid, "incr") # Fetch .config file
        ker_incr = compute_kernel(i, "incr") # Create a kernel instance corresponding to the physical kernel freshly compiled.
        if ker_incr == -1:
            print("Error while retrieving incremental kernel from database")
            exit(1)

        dock_basic = execute_config(i) # Run a basic compilation with the .config file retrieves from the incremental compilation
        fetch_files(i, dock_basic, "basic") # Fetch .config file
        print("")
        ker_basic = compute_kernel(i, "basic")  # Create a new kernel instance attributed to the kernel compiled in basic mode
        if ker_basic == -1:
            print("Error while retrieving basic kernel from database")
            exit(1)

        incremental.append(ker_incr)
        basic.append(ker_basic)

    result = compare(incremental, basic)
    print(result)
    subprocess.run("./clean.py --docker", shell=True)
