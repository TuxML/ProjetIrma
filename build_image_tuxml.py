#!/usr/bin/python3

## @file build_image_tuxml.py
# @author DIDOT Gwendal ACHER Mathieu PICARD Michaël
# @copyright Apache License 2.0
# @brief Script use to simplified creation and uses of Docker images.
# @details This script was design to help members of the TuxML project to easily use Docker, without any knowledge require
#  other than what a Docker image is (check https://docs.docker.com/get-started/ for more information).

import subprocess
import os

## docker_build
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief build a docker image
# @param image The image name of your choice. Default to None.
# @param tag The tag of your choice. Default to None.
# @param path The path where the Dockerfile is. Default to None, which is
# equivalent to . (current directory).
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


## create_dockerfile
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief Create and save a Dockerfile
# @param content What you will actually put in your Dockerfile. Default to None.
# @param path Where you want to save your Dockerfile. Default to None, which is
# # equivalent to . (current directory).
def create_dockerfile(content=None, path=None):
    if path is not None:
        os.chdir(path)

    with open("Dockerfile", "w") as file:
        file.write(content)




