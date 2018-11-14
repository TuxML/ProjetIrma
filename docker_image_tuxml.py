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
from settings_image_tuxml import *


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
    str_build = "docker build".format(image)
    if image is not None:
        str_build = "{} -t {}".format(str_build, image)
        if tag is not None:
            str_build = "{}:{}".format(str_build, tag)
    str_build = "{} {}".format(str_build, path)
    subprocess.run(str_build, shell=True)


## docker_push
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief push a docker image
# @param image The name of the image to push.
# @param tag The tag of the image to push.
def docker_push(image, tag=None):
    str_push = "docker push {}".format(image)
    if tag is not None:
        str_push = "{}:{}".format(str_push, tag)
    result_push = subprocess.call(args=str_push, shell=True)
    if result_push == 1:
        print("You need to login on Docker hub\n")
        subprocess.run(args="docker login", shell=True)
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
    get_linux_kernel(LINUX_KERNEL, tmp_location)
    content = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        CONTENT_BASE_IMAGE['DEBIAN_VERSION'],
        CONTENT_BASE_IMAGE['MKDIR_TUXML'],
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
# TODO: creation of Tuxml.tar.gz beforehand.
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
        tmp_content['RUN_DEP_FILE'] = "RUN echo {} >> /dependencies.txt".format(str_dep)
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
        image=NAME_IMAGE,
        tag=tag,
        path=tmp_location)


## create_big_image_tuxml_uncompressed
# @author PICARD Michaël
# @version 1
# @brief Create the uncompressed image to work with.
# @param tmp_location Where we create and build the image.
# @param tag The tag of the built image. Default to None.
# @param dependencies_path The path to the file corresponding to optional
# dependencies. Default to None.
def create_big_image_tuxml_uncompressed(tmp_location, tag=None):
    content = "{}".format(CONTENT_BIG_IMAGE['PREVIMG_VERSION'])
    if tag is not None:
        content = "{}:{}".format(content, tag)
    content = "{}\n{}\n{}\n{}\n{}\n{}".format(
        content,
        CONTENT_BIG_IMAGE['TUXML_UNTAR'],
        CONTENT_BIG_IMAGE['LINUX_UNTAR'],
        CONTENT_BIG_IMAGE['RUN_DEP_FILE'],
        CONTENT_BIG_IMAGE['EXPOSE'],
        CONTENT_BIG_IMAGE['ENV_NAME']
    )
    create_dockerfile(content=content, path=tmp_location)
    docker_build(
        image=NAME_BIG_IMAGE,
        tag=tag,
        path=tmp_location
    )


## exist_sub_image_tuxml_compressed
# @author PICARD Michaël
# @version 1
# @brief Test if the sub_image_tuxml_compressed docker image already exist.
# @return Boolean
def exist_sub_image_tuxml_compressed():
    cmd = "docker image ls --format {{.Repository}} | grep"
    cmd = "{} {}".format(cmd, NAME_BASE_IMAGE)
    # mpicard: grep return 0 if a line is found, 1 is no line found and 2 or
    # greater if an error occured. So we just check it.
    returncode = subprocess.call(
        args=cmd,
        shell=True
    )
    return returncode == 0


##get_linux_kernel
# @author POLES Malo, PICARD Michaël
# @version 2
# @brief Download the linux kernel at the current location
# @param name Specify version of kernel we want. MUST BE A v4.x version.
def get_linux_kernel(name, path=None):
    if path is not None:
        os.chdir(path)
    name += ".tar.xz"
    list_dir = os.listdir('.')
    if name not in list_dir:
        print("Linux kernel not found, downloading...")
        wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/{}".format(name)
        subprocess.run(args=wget_cmd, shell=True)
    else:
        print("Linux kernel found.")


## ask_for_confirmation
# @author POLES Malo, PICARD Michaël
# @version 2
# @brief Ask a confirmation, and return the answer as boolean
# @return Boolean
def ask_for_confirmation():
    answer = input().lower()
    while answer != 'n' and answer != 'y':
        print("y/n")
        answer = input().lower()
    return answer == 'y'


## create_tuxml_archive
# @author THOMAS Luis, PICARD Michaël
# @version 1
# @brief Pack all necessary file inside the archive TuxML.tar.xz
def create_tuxml_archive(path):
    list_file = [
        "core/*",
        "dependences.txt",
        "core-correlation",
        "inDocker/*"
    ]
    cmd = "mkdir {}/TuxML".format(path)
    subprocess.call(args=cmd, shell=True)
    cmd = "cp -r {} {}/TuxML".format(
        " ".join(
            list(map(
                lambda x: "{}/{}".format(
                    os.path.dirname(os.path.abspath(__file__)),
                    x),
                list_file
            ))),
        path
    )
    subprocess.call(args=cmd, shell=True)

    os.chdir("{}/TuxML".format(path))
    subprocess.call(args="tar -cf TuxML.tar.xz *", shell=True)
    subprocess.call(args="mv TuxML.tar.xz ../TuxML.tar.xz", shell=True)
    os.chdir("..")
    subprocess.call(args="rm -rf TuxML", shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-p',
        '--push',
        help="Push the image on the distant repository",
        action="store_true"
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
             "in most of the case.",
        action="store_true"
    )
    parser.add_argument(
        "-l",
        "--location",
        help="Where you want to create your directory to generate/build. Default is current",
        default="."
    )

    args = parser.parse_args()

    if args.push:
        docker_push(NAME_IMAGE, args.tag)
    else:
        if not exist_sub_image_tuxml_compressed():
            create_sub_image_tuxml_compressed(args.location)
        elif args.full_rebuild:
            print("Are you sure that you want to rebuild the whole docker image"
                  " project (Y/n)? ")
            if ask_for_confirmation():
                create_sub_image_tuxml_compressed(args.location)
            else:
                print("Whole rebuild canceled.\n")
        create_tuxml_archive(args.location)
        create_image_tuxml_compressed(args.location, args.tag, args.dependencies)
        create_big_image_tuxml_uncompressed(args.location, tag=args.tag)
        os.remove("{}/TuxML.tar.xz".format(args.location))
