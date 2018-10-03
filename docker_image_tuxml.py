#!/usr/bin/python3

## @file build_image_tuxml.py
# @author DIDOT Gwendal ACHER Mathieu PICARD Michaël
# @copyright Apache License 2.0
# @brief Script use to simplified creation and uses of Docker images.
# @details This script was design to help members of the TuxML project to easily
# use Docker, without any knowledge require other than what a Docker image is
# (check https://docs.docker.com/get-started/ for more information).

import argparse
import subprocess
import os
from .settings_image_tuxml import *


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
    str_build = "sudo docker build".format(image)
    if image is not None:
        str_build = "{} -t {}".format(str_build, image)
        if tag is not None:
            str_build = "{}:{}".format(str_build, tag)
    str_build = "{} {}".format(str_build, path)
    print("command : {}".format(str_build))
    subprocess.call(args=str_build)


## docker_push
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief push a docker image
# @param image The name of the image to push.
# @param tag The tag of the image to push.
def docker_push(image, tag=None):
    str_push = "sudo docker push {}".format(image)
    if tag is not None:
        str_push += "{}:{}".format(str_push, tag)
    print("command : {}".format(str_push))
    result_push = subprocess.call(args=str_push, shell=True)
    if result_push == 1:
        print("You need to login on Docker hub\n")
        subprocess.call(args="sudo docker login", shell=True)
        docker_push(image=image, tag=tag)


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


## create_sub_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Create a base image to speed our usual build
# @details It create an image on which we will build the image to upload. Its
# goal is to speed up the creation context when we just update project's files,
# and not the whole dependencies for our project.
def create_sub_image_tuxml_compressed(tmp_location):
    create_dockerfile(
        content=CONTENT_BASE_IMAGE,
        path=tmp_location)
    docker_build(
        image=NAME_BASE_IMAGE,
        path=tmp_location)


## create_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Create the compressed image to work with.
# @param tmp_location Where we create and build the image.
# @param tag The tag of the built image. Default to None.
# @param dependencies_path The path to the file corresponding to optional
# dependencies. Default to None.
def create_image_tuxml_compressed(tmp_location, tag=None, dependencies_path=None):
    content = CONTENT_IMAGE
    if dependencies_path is not None:
        with open(dependencies_path) as dep_file:
            str_dep = ''
            tmp = dep_file.readline()
            while (tmp != ''):
                str_dep += tmp + " "
                tmp = dep_file.readline()
            str_dep = str_dep.replace("\n", "")
        content = "{}\n" \
                  "RUN apt-get update && apt-get -qq -y install {} ".format(
                    content, str_dep)
    create_dockerfile(
        content=content,
        path=tmp_location)
    docker_build(
        image=NAME_BASE_IMAGE,
        tag=tag,
        path=tmp_location)


## exist_sub_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Test if the sub_image_tuxml_compressed docker image already exist.
def exist_sub_image_tuxml_compressed():
    list_str_test = ["docker", "image", "ls", "--format", "{{.Repository}}"]
    result = subprocess.check_output(
        args=list_str_test
    )
    result = result.decode('UTF-8')
    result.splitlines()
    try:
        result.index(NAME_BASE_IMAGE)
        return True
    except:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-p',
        '--push',
        help="Push the image on the distant repository")
    parser.add_argument(
        '-t',
        '--tag',
        help="Tag of the image you want to generate/build/push",
        default="dev")
    parser.add_argument(
        '-dep',
        '--dependencies',
        help="Dependencies you want to add to your docker image when you "
             "generate your dockerfile")
    parser.add_argument(
        '-f',
        '--full_rebuild',
        help="Force the rebuild of the core system image, which is not needed "
             "in most of the case."
    )

    args = parser.parse_args()

    if args.push:
        docker_push(NAME_IMAGE, args.tag)
    else:
        # TODO : Replace with the create tmp_location method
        tmp_location = '.'

        if args.full_rebuild:
            print("Are you sure that you want to rebuild the whole docker image"
                  "project (Y/n)? ")
            answer = input()
            answer.lower()
            if answer == "Y" or answer == "y":
                create_sub_image_tuxml_compressed(tmp_location)
            else:
                print("Whole rebuild canceled.\n")
        elif not exist_sub_image_tuxml_compressed():
            create_sub_image_tuxml_compressed(tmp_location)
        create_image_tuxml_compressed(tmp_location, args.tag, args.dependencies)
