#!/usr/bin/python3

import sys
import os
import time
import subprocess
import argparse

NB_DOCKERS = 0
DOCKER_IMGS = ["micleb/debiantuxml:latest"] # list of docker images
VERBOSE = 1
OUTPUT = subprocess.DEVNULL
TUXML_PATH = "/TuxML/"
TUXLOGS = TUXML_PATH + "Logs/"
KDIR = TUXML_PATH + "linux-4.13.3/"
KLOGS = KDIR + "logs/"


def args_handler():
    global NB_DOCKERS, OUTPUT

    msg  = "Welcome, this is the launcher.\n\n"

    n_help  = "number of dockers to launch, minimum 1, maximum 50"
    v_help  = "increase or decrease output verbosity\n"
    v_help += " " * 2 + "0 : quiet\n"
    v_help += " " * 2 + "1 : normal\n"
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


def docker_pull_image(i):
    print("==> Recovering latest docker image")
    status = subprocess.call(["docker pull " + DOCKER_IMGS[i]], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0


def git_fetch_and_checkout(i):
    print("==> Downloading TuxML repository")

    git_cmd = "'cd " + TUXML_PATH + "; git fetch; git checkout dev'"
    cmd = "docker run -it " + DOCKER_IMGS[i] + " sh -c " + git_cmd
    status = subprocess.call([cmd], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0


def docker_run_image(i, launch_time):
    sh  = "'cd " + TUXML_PATH + ";"
    sh += "git fetch;"
    sh += "git checkout dev;"
    sh += "./tuxLogs.py'"

    cmd = "docker run -it " + DOCKER_IMGS[i] + " bash -c " + sh

    print("==> Running docker #{0:02d} ".format(i+1))
    print(cmd)
    print("+" + "-" * 78 + "+")
    status = subprocess.call([cmd], shell=True)
    print("+" + "-" * 78 + "+")

    if status != 0:
        return -1
    else:
        return 0


def docker_cp_logfiles(docker_id, launch_time):
    print("==> Copying logfiles to " + TUXLOGS + launch_time + "/ ...")
    logfiles = [KLOGS + "std.log", KLOGS + "err.log", KDIR + ".config", TUXML_PATH + "output.log"]

    for logfile in logfiles:
        cmd = "docker cp " + docker_id + ":" + logfile + " " + TUXLOGS + launch_time + "/"
        status = subprocess.call([cmd], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0


def main():
    args_handler()

    if not os.path.exists(TUXLOGS):
        os.makedirs(TUXLOGS)

    for i in range(0, NB_DOCKERS):
        if docker_pull_image(i % len(DOCKER_IMGS)) != 0:
            sys.exit(-1)

        # if git_fetch_and_checkout(i % len(DOCKER_IMGS)) != 0:
        #     sys.exit(-1)

        launch_time = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
        os.makedirs(TUXLOGS + launch_time)

        if docker_run_image(i % len(DOCKER_IMGS), launch_time) != 0:
            sys.exit(-1)

        # docker_id = os.popen("docker ps -lq", "r").read()[0:-1]
        # if docker_cp_logfiles(docker_id, launch_time) != 0:
        #     sys.exit(-1)


    print("end")

# ============================================================================ #


if __name__ == '__main__':
    main()
