#!/usr/bin/python3

import sys
import os
import time
import subprocess
import argparse


NB_DOCKERS  = 0
DOCKER_IMGS = ["micleb/debiantuxml:latest"] # list of docker images
VERBOSE     = 1
OUTPUT      = subprocess.DEVNULL
TDIR        = "/TuxML/"
TLOGS       = TDIR + "logs/"
KDIR        = TDIR + "linux-4.13.3/"
KLOGS       = KDIR + "logs/"


def args_handler():
    global NB_DOCKERS, OUTPUT

    msg  = "Welcome, this is the launcher.\n\n"

    n_help  = "number of dockers to launch, minimum 1, maximum 50"
    v_help  = "increase or decrease output verbosity\n"
    v_help += " " * 2 + "0 : quiet\n"
    v_help += " " * 2 + "1 : normal (default)\n"
    v_help += " " * 2 + "2 : chatty\n"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("nbdockers", help=n_help, metavar="NB_DOCKERS", type=int)

    parser.add_argument("-v", "--verbose", help=v_help, type=int, choices=[0,1,2])
    args = parser.parse_args()

    # ask root credentials
    if os.getuid() != 0:
          sudo_args = ["sudo", sys.executable] + sys.argv + [os.environ]
          os.execlpe('sudo', *sudo_args)
          sys.exit(-1)

    v_min = 1
    if args.nbdockers < v_min:
        parser.error("Minimum value for NB_DOCKERS is {}".format(v_min))

    v_max = 50
    if args.nbdockers > v_max:
        parser.error("Maximum value for NB_DOCKERS is {}".format(v_max))

    NB_DOCKERS = args.nbdockers

    # manage level of verbosity
    if args.verbose:
        VERBOSE = args.verbose

        if VERBOSE > 1:
            OUTPUT = sys.__stdout__
    else:
        VERBOSE = 1


def start_container(i):
    print("==> Recovering latest docker image")
    status = subprocess.call(["docker pull " + DOCKER_IMGS[i]], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0


def start_tuxml(docker_id, i):
    print("==> Running docker #{0:02d} ".format(i+1))
    print("+" + "-" * 78 + "+")
    cmd = "docker run -it " + docker_id + "./launcher.sh"
    status = subprocess.call([cmd], shell=True)
    print("+" + "-" * 78 + "+")

    if status != 0:
        return -1
    else:
        return 0


def get_logfiles(docker_id, launch_time):
    print("==> Copying log files to " + TLOGS + launch_time + "/")

    os.makedirs(TLOGS + launch_time)
    logfiles = [KLOGS + "std.log", KLOGS + "err.log", KDIR + ".config", TLOGS + "output.log"]

    for logfile in logfiles:
        cmd = "docker cp " + docker_id + ":" + logfile + " " + TLOGS + launch_time + "/"
        status = subprocess.call([cmd], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0

def clean_containers():
    print("==> Cleaning containers")
    status = subprocess.call(["docker rm -v $(docker ps -aq)"], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0

def main():
    args_handler()

    if not os.path.exists(TLOGS):
        os.makedirs(TLOGS)

    for i in range(0, NB_DOCKERS):
        if start_container(i % len(DOCKER_IMGS)) != 0:
            sys.exit(-1)

        docker_id = os.popen("docker ps -lq", "r").read()[0:-1]
        launch_time = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))

        if start_tuxml(docker_id, i % len(DOCKER_IMGS)) != 0:
            sys.exit(-1)

        if get_logfiles(docker_id, launch_time) != 0:
            sys.exit(-1)

        if clean_containers() != 0:
            sys.exit(-1)


# ============================================================================ #


if __name__ == '__main__':
    main()
