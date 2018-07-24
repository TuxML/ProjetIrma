#!/usr/bin/env python2.7

import argparse
import subprocess
import os


def run():

    assert os.path.isfile("./spring.sh"), "'spring.sh' does not exist"

    null = subprocess.call("oarsub -S ./spring.sh", shell=True)
    if null == -1:
        print("Error during the call of 'spring.sh'")


def generate(args):

    nb_core = args.nb_core
    walltime = args.walltime
    nb_cpu = 1

    if nb_core <= 0:
        print("nb_core set at " + str(nb_core) +
              " --> default value restored: core=4")
        nb_core = 4

    if nb_core > 4:
        nb_cpu = nb_core / 4

    tmp = walltime.split(":")

    if len(tmp[1]) == 1:
        tmp[1] = "0" + tmp[1]

    if len(tmp[2]) == 1:
        tmp[2] = "0" + tmp[2]

    if len(tmp[0]) == 2:
        if tmp[0][0] == '0':
            tmp[0] = tmp[0][1:]

    walltime = ":".join(tmp)

    if not len(tmp) == 3 or not all([x.isdigit() for x in tmp]) or walltime == "0:00:00":
        print("walltime error \"" + str(walltime) +
              "\" --> default value restored: walltime=1:00:00")
        walltime = "1:00:00"

    assert os.path.isfile(
        "spring_core.txt"), "The core program of 'spring.sh' from 'spring_core.txt' does not exist"

    with open("spring.sh", "w") as spring:
        with open("spring_core.txt", "r") as core:

            OAR_cores = "#OAR -l /nodes=1/core=%s,walltime=%s\n" % (
                nb_core, walltime)

            lines = core.read()
            assert lines, "'spring_core.txt should not be empty'"

            spring.write("#!/bin/bash\n")
            spring.write(OAR_cores)
            spring.write("#OAR -p virt='YES'\n")
            spring.write(lines)


def setting(args):
    with open("params.txt", "w") as file:
        for i in range(args.nm):
            file.write(str(args.nc) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nc", "--number_of_compilations", type=int,
                        help="Number of compilations to do", default=1)
    parser.add_argument("--nm", "--number_of_machines", type=int,
                        help="Number of Machines to use", default=1)
    parser.add_argument("--nb-core", type=int,
                        help="Number of cores to use", default=4)
    parser.add_argument("--walltime", type=str,
                        help="Maximum time of life. (hh:mm:ss) ", default="1:00:00")
    args = parser.parse_args()

    print(" | ".join([k + ' : ' + str(vars(args)[k]) for k in vars(args)]))

    setting(args)

    generate(args)

    run()


if __name__ == '__main__':
    main()
