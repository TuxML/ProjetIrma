#!/usr/bin/env python3

import argparse
import subprocess
import re
import MySQLdb
import os
import csv
from core import tuxml_settings as tset
import flash_compare

# Class kernel to compare two of them
class kernel:

    def __init__(self, entry):
        if not len(entry) == 0:
            self.entry = entry
        else:
            self.entry = ["-1"] * 11
            self.entry[8] = " , ".join(["-1 : -1"] * 18)


    def get_cid(self):
        return str(self.entry[0])

    def get_entry(self):
        return self.entry

    def kernel2csv(self):

        final = list([self.entry[0]] + [str(self.entry[1])] + [str(self.entry[2])] + [self.entry[7]])

        compressed = self.entry[8].split(" , ")
        parse_array = []
        cprss = []

        if compressed:
            parse_array = [i.split(" : ") for i in compressed]

        if parse_array:
            cprss = [fin[1] for fin in parse_array]

        final += cprss

        return final

# Create a new kernel instance from the physical kernel
def compute_kernel(id, mode):

    cid = -1

    with open('compare/'+ str(id) + '/' + mode + '-output.log', 'r') as file:

        for line in file:

            if mode=="incr":
                match = re.search('INCREMENTAL CONFIGURATION ID #0=(\d+)', line)
            else:
                match = re.search('DATABASE CONFIGURATION ID=(\d+)', line)

            if match:
                cid = match.group(1)

        if not cid == -1:
            socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "IrmaDB_prod")
            cursor = socket.cursor()
            print("CID Used:", cid)
            query = "SELECT * FROM Compilations WHERE cid = " + cid
            cursor.execute(query)
            entry = cursor.fetchone()

            cursor.close()
            socket.close()

            return kernel(entry)

        else:
            print("Failed to retrieves CID")
            return kernel([])


# Basic compilation based on .config file from incremental
def execute_config(id):
    # Create a new container
    subprocess.run("sudo docker run -i -d tuxml/tuxmldebian:dev", shell=True, stdout=subprocess.DEVNULL)
    # Copy on it the .config file to use
    subprocess.run("sudo docker cp ./compare/" + str(id) + "/.config $(sudo docker ps -lq):/TuxML/.config", shell=True)
    # Run the compilation with the .config file from the incremental compilation
    subprocess.run("sudo docker exec -t $(sudo docker ps -lq) /TuxML/runandlog.py --path /TuxML/.config", shell=True)


def compilations(args):

    max_number = len([name for name in os.listdir('./compare/')])

    with open("csv_kernels/kernels_compare.csv", 'a') as file:
        writer = csv.writer(file)

        extension = [".gz", ".bz2", ".lzma", ".xz", ".lzo", ".lz4"]

        if not args.rewrite == -1:
            max_number = 0

        if not args.recompile == -1:
            max_number = 0

        for i in range(max_number, max_number + args.compare_number):
            if (not args.recompile == -1 and i == args.recompile) or (not args.rewrite == -1 and i == args.rewrite) or (args.rewrite == -1 and args.recompile == -1):
                os.makedirs("./compare/" + str(i), exist_ok=True)
                print("\nDirectory", i, flush=True)

                path = ""
                if not args.recompile == -1:
                    path = "--path compare/" + str(i) + "/.config"

                subprocess.run("sudo ./MLfood.py 1 1 --dev --no-clean " + path, shell=True)
                subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/output.log compare/" + str(i) + "/incr-output.log" , shell=True)
                subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/logs/err.log compare/" + str(i) + "/incr-err.log" , shell=True)
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
                subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/logs/err.log compare/" + str(i) + "/basic-err.log" , shell=True)

                if not args.no_kernel:
                    # retrieves differents possible kernels according to their names
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/basic-vmlinux", shell=True, stderr=subprocess.DEVNULL)
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/basic-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
                    subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/basic-bzImage", shell=True, stderr=subprocess.DEVNULL)
                    for ext in extension:
                        subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/basic-vmlinux.bin" + ext, shell=True)

                print("\nComputing kernel basic", flush=True)
                basekernel = compute_kernel(i, "basic")

                print("\nComputing .config values", flush=True)

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
        subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/logs/err.log compare/" + str(i) + "/incr-err.log" , shell=True)

        if not args.no_kernel:
            # retrieves differents possible kernels according to their names
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/incr-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/incr-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/incr-bzImage", shell=True, stderr=subprocess.DEVNULL)
            for ext in extension:
                subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/incr-vmlinux.bin" + ext, shell=True, stderr=subprocess.DEVNULL)

        execute_config(i)
        subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/output.log compare/" + str(i) + "/basic-output.log" , shell=True)
        subprocess.run("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/logs/err.log compare/" + str(i) + "/incr-err.log" , shell=True)

        if not args.no_kernel:
            # retrieves differents possible kernels according to their names
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/vmlinux ./compare/" + str(i) + "/basic-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux ./compare/" + str(i) + "/basic-compressed-vmlinux", shell=True, stderr=subprocess.DEVNULL)
            subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/bzImage ./compare/" + str(i) + "/basic-bzImage", shell=True, stderr=subprocess.DEVNULL)
            for ext in extension:
                subprocess.call("sudo docker cp $(sudo docker ps -lq):/TuxML/linux-4.13.3/arch/x86/boot/compressed/vmlinux.bin" + ext + " ./compare/" + str(i) + "/basic-vmlinux.bin" + ext, shell=True, stderr=subprocess.DEVNULL)


def create_header():

    conn = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "IrmaDB_prod")
    cursor = conn.cursor()

    get_prop = "SELECT name, type FROM Properties"
    # Extract properties
    cursor.execute(get_prop)
    types_results = list(cursor.fetchall())

    if len(types_results) == 0:
        print("\nError : Properties not present in database - You need to run Kanalyser first (https://github.com/TuxML/Kanalyser)")

    cursor.close()
    conn.close()

    # .config column names
    names = [""]*len(types_results)
    index = 0
    for (name, typ) in types_results:
        names[index] = name
        index += 1

    with open("csv_kernels/kernels_compare.csv", "w") as f:
        head = ("cid,date,time,vmlinux,GZIP-bzImage,GZIP-vmlinux,GZIP,BZIP2-bzImage,BZIP2-vmlinux,BZIP2,LZMA-bzImage,LZMA-vmlinux,LZMA,XZ-bzImage,XZ-vmlinux,XZ,LZO-bzImage,LZO-vmlinux,LZO,LZ4-bzImage,LZ4-vmlinux,LZ4,basic-cid,basic-date,basic-time,basic-vmlinux,basic-GZIP-bzImage,basic-GZIP-vmlinux,basic-GZIP,basic-BZIP2-bzImage,basic-BZIP2-vmlinux,basic-BZIP2,basic-LZMA-bzImage,basic-LZMA-vmlinux,basic-LZMA,basic-XZ-bzImage,basic-XZ-vmlinux,basic-XZ,basic-LZO-bzImage,basic-LZO-vmlinux,basic-LZO,basic-LZ4-bzImage,basic-LZ4-vmlinux,basic-LZ").split(",") #," + ",".join(names)).split(",")

        writer = csv.DictWriter(f, head)
        writer.writeheader()
        print("csv_kernels/kernels_compare.csv created", flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("compare_number",type=int, help="The number of comparaison between a basic compilation and a incremental one.\nThe bigger it is, the better")
    parser.add_argument("--no-kernel", help="Retrieves kernel and compressed kernels", action="store_true")
    parser.add_argument("--rewrite", type=int, help="Rewrite the given number of the directory with new kernels to compare", default=-1)
    parser.add_argument("--recompile", type=int, help="Re-compile a given .config to ensure the result", default=-1)
    parser.add_argument("--fix-errors", help="Correct all failed compilations", action="store_true")
    args = parser.parse_args()

    if not os.path.exists("./compare/"):
        os.makedirs("./compare/")

    max = len([name for name in os.listdir('./compare/')])

    if args.recompile > max:
        args.recompile = max

    if args.recompile < 0:
        args.recompile = -1

    if not args.rewrite == -1:
        args.compare_number = args.rewrite + 1

    if not args.recompile == -1:
        args.compare_number = args.recompile + 1

    # print(" ".join([k + ' : ' + str(vars(args)[k]) for k in vars(args)]), flush=True)

    if not os.path.exists("csv_kernels/kernels_compare.csv"):
        create_header()

    compilations(args)
    max = len([name for name in os.listdir('./compare/')])

    err, average = flash_compare.diff_size(max)
    # Repeat to replace the compilations errors with correct values from successed compilations
    if (not args.rewrite == -1 and not args.recompile == -1) or args.fix_errors:
        while not len(err) == 0:
            print("\nErrors to correct:", len(err), flush=True)
            fix_err(err, args)
            err,average = flash_compare.diff_size(max)

    print("Size average:", average, flush=True)
    print("Differences of sizes done in compare/X/diff.txt", flush=True)

    diff_time, time_average = flash_compare.diff_time(max)

    msg = ""
    if time_average >= 0:
        tmp = str(time_average).split(".")
        time_average = tmp[0] + "." + tmp[1][:3]
        msg = "The average time \033[0;32mgained\033[0m is %s seconds"

    else:
        time_average = abs(time_average)
        tmp = str(time_average).split(".")
        time_average = tmp[0] + "." + tmp[1][:3]
        msg = "The average time \033[0;31mlose\033[0m is %s seconds"

    print(msg % time_average, flush=True)

    subprocess.call("sudo chown -R $(sudo who -u | awk '{print $1}'):$(sudo who -u | awk '{print $1}') ./compare", shell=True)

if __name__ == '__main__':
    main()
