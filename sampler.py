#!/usr/bin/python3

import sys
import os
import time
import subprocess
import argparse
import random

# TODO ajouter image fedora
# TODO commentaires
# TODO mettre les help des options à 80 char

NB_DOCKERS  = 0
DOCKER_IMGS = [ "micleb/debian_tuxml_{}:latest",
                "micleb/arch_tuxml_{}:latest",
                "micleb/centos_tuxml_{}:latest"]
IMAGE       = ""
BRANCH      = ""
VERBOSE     = 1
OUTPUT      = subprocess.DEVNULL
TDIR        = "/tuxml/"
TLOGS       = TDIR + "logs/"
KDIR        = TDIR + "linux-4.13.3/"
KLOGS       = KDIR + "logs/"
NO_CLEAN    = False


def args_handler():
    global NB_DOCKERS, OUTPUT, NO_CLEAN, VERBOSE, BRANCH, IMAGE

    msg  = "The  sampler  allows   you   to   run  tuxml.py   through   many  docker  images\n"
    msg += "sequentially.\n"
    msg += "At the end of the compilation, the sampler retrieves  the  logs (stdout, stderr,\n"
    msg += "tuxml's output  and  kconfig file)  from  the  docker  container  and  save them\n"
    msg += "to the Tuxml/logs folder.\n\n"

    n_help  = "number of dockers to launch, minimum 1"
    v_help  = "increase or decrease output verbosity\n"
    v_help += " " * 2 + "0 : quiet\n"
    v_help += " " * 2 + "1 : normal (default)\n"
    v_help += " " * 2 + "2 : chatty\n"
    nc_help = "do not clean containers"
    i_help  = "two kinds of images are available\n"
    i_help += " " * 2 + "prod : TuxML is  already included in the docker image.\n"
    i_help += " " * 9 + "This is the fastest way. (default)\n"
    i_help += " " * 2 + "dev  : download  TuxML repository  from  GitHub before\n"
    i_help += " " * 9 + "starting the compilation\n"
    b_help  = "choose which  version of TuxML to  execute between\n"
    b_help += "master and dev\n"
    b_help += " " * 2 + "master : last stable version (default)\n"
    b_help += " " * 2 + "dev    : last up-to-date version\n"
    V_help  = "display the sampler version and exit"

    parser = argparse.ArgumentParser(description=msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("nbdockers", help=n_help, metavar="NB_DOCKERS", type=int)

    parser.add_argument("-b", "--branch", help=b_help, metavar="BRANCH", choices=["master", "dev"], default="master")
    parser.add_argument("-i", "--image", help=i_help, metavar="IMAGE", choices=["prod", "dev"], default="prod")
    parser.add_argument("--no-clean", help=nc_help, action="store_true")
    parser.add_argument("-V", "--version", help=V_help, action='version', version='%(prog)s pre-alpha v0.3')
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

    NB_DOCKERS = args.nbdockers
    IMAGE      = args.image
    BRANCH     = args.branch
    NO_CLEAN   = args.no_clean

    if args.image == "prod":
        print("Prod images are currently not availables")
        sys.exit(-1)

    # manage level of verbosity
    if args.verbose:
        VERBOSE = args.verbose

        if VERBOSE > 1:
            OUTPUT = sys.__stdout__
    else:
        VERBOSE = 1


def download_docker_image(docker_img):
    print("==> Recovering latest docker image")
    status = subprocess.call(["docker pull " + docker_img], stdout=OUTPUT, stderr=OUTPUT, shell=True)

    if status != 0:
        print("--> Error\n")
        return -1
    else:
        print("--> Done\n")
        return 0


def run_tuxml(docker_img, i):
    print("==> Running docker #{0:02d}".format(i+1) + " on " + docker_img)

    cmd  = "'cd {};".format(TDIR)
    cmd += "git fetch;"
    cmd += "git checkout {};".format(BRANCH)
    cmd += "mkdir logs;"
    cmd += "echo 'TUXML_BRANCH = {}\nTUXML_IMAGE = {}' > tuxml.conf;".format(BRANCH, IMAGE)
    cmd += "python3 -u ./core/tuxml.py linux-4.13.3/ | tee logs/output.log;'"

    print("+" + "-" * 78 + "+")
    status = subprocess.call(["docker run -it " + docker_img + " bash -c " + cmd], shell=True)
    print("+" + "-" * 78 + "+")

    if status != 0:
        return -1
    else:
        return 0


def retrieve_logs(docker_id, launch_time):
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

    print("")
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
        img = DOCKER_IMGS[random.randrange(0, len(DOCKER_IMGS), 1)].format(IMAGE)

        if download_docker_image(img) != 0:
            sys.exit(-1)

        launch_time = time.strftime("%Y%m%d_%H%M%S", time.gmtime(time.time()))
        if run_tuxml(img, i) != 0:
            sys.exit(-1)


        docker_id = os.popen("docker ps -lq", "r").read()[0:-1]
        if retrieve_logs(docker_id, launch_time) != 0:
            sys.exit(-1)

        if not NO_CLEAN:
            if clean_containers() != 0:
                sys.exit(-1)


# ============================================================================ #


if __name__ == '__main__':
    main()
