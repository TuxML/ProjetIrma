#!/usr/bin/env python3


import argparse
import subprocess
import re
import MySQLdb
import os
import csv
import core.tuxml_settings as tset
import flash_compare

# Class kernel to compare two of them
class kernel:

    def __init__(self, size, compressed, cid):
        self.size = size    # Size of kernel
        self.compressed = compressed    # Compilation kernels list
        self.cid = cid      # Cid of the kernel in Database

    def get_size(self):
        return str(self.size)

    def get_compressed(self):
        return str(self.compressed)

    def get_cid(self):
        return str(self.cid)

# Example of formatted compressed_sizes:
#
# "GZIP-bzImage : 6726608 , GZIP-vmlinux : 8811992 , GZIP : 6580441 , BZIP2-bzImage : 10433488 ,
# BZIP2-vmlinux : 12518312 , BZIP2 : 6167633 , LZMA-bzImage : 5346256 , LZMA-vmlinux : 7431120 ,
# LZMA : 5209210 , XZ-bzImage : 4662224 , XZ-vmlinux : 6747512 , XZ : 4515160 , LZO-bzImage : 7406544 ,
# LZO-vmlinux : 9491320 , LZO : 7271308 , LZ4-bzImage : 7934928 , LZ4-vmlinux : 10020016 , LZ4 : 7785825"

    def kernel2csv(self):
        compressed = self.get_compressed().split(" , ")
        parse_array = [i.split(" : ") for i in compressed]
        final = [fin[1] for fin in parse_array]

        final.insert(0, self.get_size())

        return final


    def pprint(self):
        return "Cid: " + str(self.cid) + "\nSize: " + str(self.size) + "\nCompressed kernels sizes: " + str(self.compressed)


# Create a new kernel instance from the physical kernel
def compute_kernel(id, mode):

    cid = -1

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

        size = entry[7] # Size of kernel column
        compressed = entry[8] # Compressed kernels size column

        cursor.close()
        socket.close()

        return kernel(size,compressed,cid)

    else:
        print("Failed to retrieves CID")
        return kernel(-1,-1,-1)


# Basic compilation based on .config file from incremental
def execute_config(id):
    # Create a new container
    subprocess.run("sudo docker run -i -d tuxml/tuxmldebian:dev", shell=True, stdout=subprocess.DEVNULL)
    # Copy on it the .config file to use
    subprocess.run("sudo docker cp ./compare/" + str(id) + "/.config $(sudo docker ps -lq):/TuxML/.config", shell=True)
    # Run the compilation with the .config file from the incremental compilation
    subprocess.run("sudo docker exec -t $(sudo docker ps -lq) /TuxML/runandlog.py --path /TuxML/.config", shell=True)


def compilations(args):

    with open("csv/kernels_compare.csv", 'a') as file:
        writer = csv.writer(file)

        extension = [".gz", ".bz2", ".lzma", ".xz", ".lzo", ".lz4"]

        ker = "--no-kernel" if args.no_kernel else "--fetch-kernel"
        for i in range(args.compare_number):
            if (not args.rewrite == -1 and i == args.rewrite) or (args.rewrite == -1):
                os.makedirs("./compare/" + str(i), exist_ok=True)
                subprocess.run("sudo ./MLfood.py 1 1 --dev --no-clean " + ker, shell=True)
                subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/output.log compare/" + str(i) + "/incr-output.log" , shell=True)
                subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/.config compare/" + str(i) + "/.config" , shell=True)

                if not args.no_kernel:
                    # retrieves differents possible kernels according to their names
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/incr-vmlinux", shell=True, stderr=subprocess.DEVNULL)
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/incr-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/incr-bzImage", shell=True, stderr=subprocess.DEVNULL)
                    for ext in extension:
                        subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/incr-vmlinux.bin" + ext, shell=True)

                print("Computing kernel incr", flush=True)
                inkernel = compute_kernel(i, "incr")

                execute_config(i)
                subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/output.log compare/" + str(i) + "/basic-output.log" , shell=True)
                if not args.no_kernel:
                    # retrieves differents possible kernels according to their names
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/basic-vmlinux", shell=True, stderr=subprocess.DEVNULL)
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/basic-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/basic-bzImage", shell=True, stderr=subprocess.DEVNULL)
                    for ext in extension:
                        subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/basic-vmlinux.bin" + ext, shell=True)

                print("Computing kernel basic", flush=True)
                basekernel = compute_kernel(i, "basic")

                entry = inkernel.kernel2csv() + basekernel.kernel2csv()

                writer.writerow(entry)

                # Stop the container Docker and erase it
                subprocess.run("sudo ./clean.py --docker", shell=True)

def fix_err(err, args):
    extension = [".gz", ".bz2", ".lzma", ".xz", ".lzo", ".lz4"]

    for i in err:
        print("Fixing ...", i, flush=True)
        os.makedirs("./compare/" + str(i), exist_ok=True)
        subprocess.run("sudo ./MLfood.py 1 1 --dev --no-clean", shell=True)
        subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/output.log compare/" + str(i) + "/incr-output.log" , shell=True)
        subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/.config compare/" + str(i) + "/.config" , shell=True)

        if not args.no_kernel:
            # retrieves differents possible kernels according to their names
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/incr-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/incr-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/incr-bzImage", shell=True, stderr=subprocess.DEVNULL)
            for ext in extension:
                subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/incr-vmlinux.bin" + ext, shell=True)

        execute_config(i)
        subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/output.log compare/" + str(i) + "/basic-output.log" , shell=True)

        if not args.no_kernel:
            # retrieves differents possible kernels according to their names
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/basic-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/basic-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/basic-bzImage", shell=True, stderr=subprocess.DEVNULL)
            for ext in extension:
                subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/basic-vmlinux.bin" + ext, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("compare_number",type=int, help="The number of comparaison between a basic compilation and a incremental one.\nThe bigger it is, the better")
    parser.add_argument("--no-kernel", help="Retrieves kernel and compressed kernels", action="store_true")
    parser.add_argument("--rewrite", type=int, help="Rewrite the given number of the directory with new kernels to compare", default=-1)
    args = parser.parse_args()

    if args.rewrite:
        args.compare_number = args.rewrite + 1

    print("\n".join([k + ' : ' + str(vars(args)[k]) for k in vars(args)]), flush=True)
    # compilations(args)

    err,average = flash_compare.diff_size(args.compare_number)
    # Repeat to replace the compilations error with real values from successed compilations
    while not len(err) == 0:
        print("\nErrors to correct:", len(err), flush=True)
        fix_err(err, args)
        err,average = flash_compare.diff_size(args.compare_number)

    print("Average:", average, flush=True)
    print("Differences of sizes done in compare/X/diff.txt", flush=True)

if __name__ == '__main__':
    main()
