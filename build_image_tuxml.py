#!/usr/bin/python3

## @file build_image_tuxml.py
# @author DIDOT Gwendal ACHER Mathieu PICARD Michaël
# @copyright Apache License 2.0
# @brief Script use to simplified creation and uses of Docker images.
# @details This script was design to help members of the TuxML project to easily use Docker, without any knowledge require
#  other than what a Docker image is (check https://docs.docker.com/get-started/ for more information).

import subprocess


def docker_build(image=None, tag=None, path=None):
    if path is None:
        path = "."
    strBuild = "sudo docker build".format(image)
    if image is not None:
        strBuild = "{} -t {}".format(strBuild, image)
        if tag is not None:
            strBuild = "{}:{}".format(strBuild, tag)
    strBuild = "{} {}".format(strBuild, path)
    print("command : {}".format(strBuild))
    subprocess.call(args=strBuild)


def create_dockerfile(content=None, path=None):
    pass


def copy_file(content=None, path=None):
    pass
