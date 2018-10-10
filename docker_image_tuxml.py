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
    content = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        CONTENT_BASE_IMAGE['DEBIAN_VERSION'],
        CONTENT_BASE_IMAGE['LINUX_TAR'],
        CONTENT_BASE_IMAGE['ENV_VARS'],
        CONTENT_BASE_IMAGE['ZONEINFO'],
        CONTENT_BASE_IMAGE['RUN_DEP'],
        CONTENT_BASE_IMAGE['RUN_DEP_FILE'],
        CONTENT_BASE_IMAGE['RUN_PIP'],
        CONTENT_BASE_IMAGE['EXPOSE'],
        CONTENT_BASE_IMAGE['ENV_NAME']
    )
    create_dockerfile(
        content=content,
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
    tmp_content = CONTENT_IMAGE
    if dependencies_path is not None:
        with open(dependencies_path) as dep_file:
            str_dep = ''
            tmp = dep_file.readline()
            while tmp != '':
                str_dep += tmp + " "
                tmp = dep_file.readline()
            str_dep = str_dep.replace("\n", "")
        tmp_content['RUN_DEP'] =\
            "RUN apt-get update && apt-get -qq -y install {} ".format(str_dep)
        tmp_content['RUN_DEP_FILE'] = "echo {} >> /dependencies.txt".format(str_dep)
    content = "{}\n{}\n{}\n{}\n{}".format(
        tmp_content['PREVIMG_VERSION'],
        tmp_content['TUXML_TAR'],
        tmp_content['RUN_DEP'],
        tmp_content['RUN_DEP_FILE'],
        tmp_content['EXPOSE'],
        tmp_content['ENV_NAME']
    )
    create_dockerfile(
        content=content,
        path=tmp_location)
    docker_build(
        image=NAME_BASE_IMAGE,
        tag=tag,
        path=tmp_location)


def create_big_image_tuxml_uncompressed(tmp_location, tag=None):
    content = "{}\n{}\n{}\n{}\n{}".format(
        CONTENT_BIG_IMAGE['PREVIMG_VERSION'],
        CONTENT_BIG_IMAGE['TUXML_TAR'],
        CONTENT_BIG_IMAGE['RUN_DEP'],
        CONTENT_BIG_IMAGE['RUN_DEP_FILE'],
        CONTENT_BIG_IMAGE['EXPOSE'],
        CONTENT_BIG_IMAGE['ENV_NAME']
    )
    create_dockerfile(content=content, path=tmp_location)
    docker_build(
        image=NAME_BASE_IMAGE,
        tag=tag,
        path=tmp_location
    )


## exist_sub_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Test if the sub_image_tuxml_compressed docker image already exist.
# TODO: Refactor to be nicer
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
    except KeyError:
        return False

## create the directory where we create the docker image
# @author POLES Malo
# @version 1
# @brief Create the directory where we want to build the docker image
# @param name Name of the directory
# @param path Location where we want to create the directory, '.' by default
# @return Return -1 if it is impossible to get to location pointed by path
#         return -2 if it is impossible to create the directory
#         return path  on success


def create_build_dir(name="docker_image_tuxml", path=None):
    if path is not None:
        try:
            os.chdir(path)
        except Exception as err:
            print("An error occur while moving to {}\n{}".format(path, err))
            return -1
    try:
        os.mkdir(name)
    except Exception as err:
        print("An error occur while trying to create the directory\n {}".format(err))
        return -2
    return os.getcwd()


##Download the linux kernel
# @author POLES Malo
# @version 1
# @brief Download the linux kernel at the current location
# @param name Specify version of kernel we want, default is 'linux-4.13.3'
# MUST BE A v4.x version
# @return Return -1 if an error occur while downloading
#         Return 0 on succes

def get_linux_kernel(name, path=None):
    if path is not None:
        try:
            os.chdir(path)
        except Exception as err:
            print("An error occur while going to location {}\n{}".format(path, err))
            return -1
    name += ".tar.xz"
    list_dir = os.listdir('.')
    if name not in list_dir:
        wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/{}".format(name)
        try:
            subprocess.call(wget_cmd, shell=True)
        except Exception as err:
            print("An error occur while trying to download {}\n {}".format(name, err))
            return -1
    return 0


def check_y_or_n():
    answer = input().lower()
    while answer != 'n' or answer != 'y':
        print("y/n")
        answer = input().lower()
    if answer == 'y':
        return True
    return False

#TODO check for relative path in settings_tuxml since Tuxml directory doesn't longer exist so it might bug
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-p',
        '--push',
        help="Push the image on the distant repository"
    )
    parser.add_argument(
        '-t',
        '--tag',
        help="Tag of the image you want to generate/build/push",
        default="dev"
    )
    parser.add_argument(
        '-dep',
        '--dependencies',
        help="Dependencies you want to add to your docker image when you "
             "generate your dockerfile"
    )
    parser.add_argument(
        '-f',
        '--full_rebuild',
        help="Force the rebuild of the core system image, which is not needed "
             "in most of the case."
    )
    parser.add_argument(
        "-l",
        "--location",
        help="Where you want to create your directory to generate/build. Default is current"
    )
    parser.add_argument(
        "-n",
        "--name",
        help="Name of the directory you want to create,docker_image_tuxml by default"
    )
    parser.add_argument(
        "-k",
        "--kernel",
        help="Specify the kernel version, default is linux-4.14.3. THIS DOESN'T WORK YET",
        default="linux-4.14.3"
    )

    args = parser.parse_args()

    if args.push:
        docker_push(NAME_IMAGE, args.tag)
    else:
        tmp_location = create_build_dir(args.name, args.location)
        if args.full_rebuild:
            print("Are you sure that you want to rebuild the whole docker image"
                  "project (Y/n)? ")
            if check_y_or_n():
                create_sub_image_tuxml_compressed(tmp_location)
            else:
                print("Whole rebuild canceled.\n")
        elif not exist_sub_image_tuxml_compressed():
            create_sub_image_tuxml_compressed(tmp_location)
        get_linux_kernel(args.kernel, tmp_location)
        create_image_tuxml_compressed(tmp_location, args.tag, args.dependencies)
        create_big_image_tuxml_uncompressed(tmp_location, tag=args.tag)
