#!/usr/bin/python3

import sys
import os
import time
import subprocess
import argparse

# TODO ajouter image fedora
# TODO commentaires

NB_DOCKERS  = 0
DOCKER_IMGS = ["micleb/debian_tuxml_{}:latest", "micleb/arch_tuxml_{}:latest"]
IMAGE       = ""
BRANCH      = ""
VERBOSE     = 1
OUTPUT      = subprocess.DEVNULL
TDIR        = "/TuxML/"
TLOGS       = TDIR + "logs/"
KDIR        = TDIR + "linux-4.13.3/"
KLOGS       = KDIR + "logs/"
NO_CLEAN    = False

def args_handler():
    global NB_DOCKERS, OUTPUT, NO_CLEAN, VERBOSE, BRANCH, IMAGE

    msg  = "The sampler allows you to run tuxml.py on many docker images.\n\n"

    n_help  = "number of dockers to launch, minimum 1, maximum 50"
    v_help  = "increase or decrease output verbosity\n"
    v_help += " " * 2 + "0 : quiet\n"
    v_help += " " * 2 + "1 : normal (default)\n"
    v_help += " " * 2 + "2 : chatty\n"
    nc_help = "do not clean containers"
    i_help  = "two kinds of images are available\n"
    i_help += " " * 2 + "prod : TuxML is  already included  in the docker\n"
    i_help += " " * 9 + "image (faster than dev)\n"
    i_help += " " * 2 + "dev  : download  TuxML  repository  from  GitHub\n"
    i_help += " " * 9 + "before starting the compilation\n"
    b_help  = "choose which  version of TuxML to  execute between\n"
    b_help += "master and dev\n"
    b_help += " " * 2 + "master : last stable version\n"
    b_help += " " * 2 + "dev    : last up-to-date version\n"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("nbdockers", help=n_help, metavar="NB_DOCKERS", type=int)
    parser.add_argument("image", help=i_help, metavar="IMAGE", choices=["prod", "dev"])
    parser.add_argument("branch", help=b_help, metavar="BRANCH", choices=["master", "dev"])

    parser.add_argument("-v", "--verbose", help=v_help, type=int, choices=[0,1,2])
    parser.add_argument("--no-clean", help=nc_help, action="store_true")
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
    IMAGE      = args.image
    BRANCH     = args.branch
    NO_CLEAN   = args.no_clean

    # manage level of verbosity
    if args.verbose:
        VERBOSE = args.verbose

        if VERBOSE > 1:
            OUTPUT = sys.__stdout__
    else:
        VERBOSE = 1


def docker_pull(i):
    print("==> Recovering latest docker image")
    status = subprocess.call(["docker pull " + DOCKER_IMGS[i].format(IMAGE)], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0


def docker_run(i):
    print("==> Running docker #{0:02d} ".format(i+1))

    cmd  = "'cd /TuxML;"
    cmd += "git fetch;"
    cmd += "git checkout {};".format(BRANCH)
    cmd += "mkdir logs;"
    cmd += "python3 -u ./core/tuxml.py linux-4.13.3/ | tee logs/output.log;'"

    print("+" + "-" * 78 + "+")
    status = subprocess.call(["docker run -it " + DOCKER_IMGS[i].format(IMAGE) + " bash -c " + cmd], shell=True)
    print("+" + "-" * 78 + "+")

    if status != 0:
        return -1
    else:
        return 0


def docker_cp(docker_id, launch_time):
    print("==> Copying log files to ./logs/" + launch_time + "/")

    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    os.makedirs("./logs/" + launch_time)
    logfiles = [KLOGS + "std.log", KLOGS + "err.log", KDIR + ".config", TLOGS + "output.log"]

    for srcfile in logfiles:
        if srcfile == KDIR + ".config":
            destfile = launch_time + ".config"
        else:
            destfile = os.path.basename(srcfile)

        cmd = "docker cp " + docker_id + ":" + srcfile + " ./logs/" + launch_time + "/" + destfile
        status = subprocess.call([cmd], stdout=OUTPUT, stderr=OUTPUT, shell=True)

        if status != 0:
            print("--> Error : {}".format(srcfile))
            return -1
        else:
            print("--> Done : {}".format(srcfile))
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
        if docker_pull(i % len(DOCKER_IMGS)) != 0:
            sys.exit(-1)

        launch_time = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
        if docker_run(i % len(DOCKER_IMGS)) != 0:
            sys.exit(-1)


        docker_id = os.popen("docker ps -lq", "r").read()[0:-1]
        if docker_cp(docker_id, launch_time) != 0:
            sys.exit(-1)

        if not NO_CLEAN:
            if clean_containers() != 0:
                sys.exit(-1)


# ============================================================================ #


if __name__ == '__main__':
    main()
