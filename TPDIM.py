#!/usr/bin/python3

## @file TPDIM.py
# @author DIDOT Gwendal ACHER Mathieu
# @copyright Apache License 2.0
# @brief Script use to simplified creation and uses of Docker images.
# @details This script was design to help members of the TuxML project to easily use Docker, without any knowledge require
#  other than what a Docker image is (check https://docs.docker.com/get-started/ for more information).

# Use 'TPDIM -h' for further informations about the options of the script

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import argparse
import subprocess

## mkGenerate
# @author ACHER Mathieu
# @param args The list of arguments given to the script
def mkGenerate(args):
    DocPre = os.listdir('.')
    if "Dockerfile" in DocPre: # We check if the dockerfile already exist and let the choice to the user to keep it or te generate a new one.
        print("It seems that a DockerFile already exist, please move it away or it will be override by the generation, do you wish to continue ? (y/n)")
        rep = input()
        rep.lower()
        if rep == "y":
            if args.dependences: # If the user give to the script a different dependences file than the default one, we use it instead
                depText = args.dependences

                with open(depText) as openDep:
                    strDep = ''
                    tmp = openDep.readline()
                    while(tmp != ''):
                        strDep = strDep + tmp + " "
                        tmp = openDep.readline()
                    strDep = strDep[:-1].replace("\n", "")

                docker_generate(args.generate, args.tag, strDep)
            else:
                docker_generate(args.generate, args.tag)
        else:
            print("Canceled")
            exit(0)


## mkBuild
#  @author ACHER Mathieu
# @param args The list of arguments give to the script
def mkBuild(args):
    if args.folder:
        DocPre = os.listdir(args.folder)
        if "Dockerfile" not in DocPre:
            print("Please give a folder with a valid Dockerfile")
            exit(-1)
        else:
            docker_build(args.build, args.tag, args.folder)
    else:
        docker_build(args.image, args.tag)


## mkPush
#  @author ACHER Mathieu
# @param args The list of arguments give to the script
def mkPush(args):
    docker_push(args.push, args.tag)

## docker_build
# @author DIDOT Gwendal
# @param image The name of the linux distribution the image is for
# @param tag The tag use to identify the image
# @param location The location of the dockerfile
## TODO test if location other than '.' work properly
def docker_build(image, tag, *location):
    print("Update of the docker image")
    # Build the choosen docker image
    if location in args:
        strBuild = 'sudo docker build -t tuxml/tuxml{}:{} {}'.format(image, tag, location)
        print(strBuild)
        pass
    else:
        strBuild = 'sudo docker build -t tuxml/tuxml{}:{} .'.format(image, tag)
    subprocess.run(strBuild, shell=True)


## dockerpush
# @author DIDOT Gwendal
# @param repository The distant repository where the user want to store the image
# @param tag The tag use to identify the image
## TODO; Let the user choose which repository he want to use instead of the TuxML Project one
def docker_push(repository, tag):
    print("Push of the image on the distant repository")
    # Push of the docker image on docker hub
    strpush = 'sudo docker push tuxml/tuxml{}:{}'.format(repository, tag)
    rstrpush = subprocess.run(strpush, shell=True).returncode
    # If needed, login to the repository
    if rstrpush == 1:
        print("You need to login on Docker hub")
        str3 = 'sudo docker login'
        subprocess.run(str3, shell=True)
        docker_push(repository, tag)


## TODO: we need to split the method in two (one for dependencies; the other for updating TUXML)
## docker_push
# @param originImage The image use to make the intermediate image
# @param tag The tag use to identify the image*
# @param dependencesFile The file use to give the dependences that have to be install by default
def docker_generate(originImage, tag, dependencesFile=None):
    newImage = 'tuxml/{}tuxml:{}'.format(originImage, tag)

    os.chdir('./BuildImageInter')

    dockerFileI = open("Dockerfile", "w")
    dockerFileI.write("FROM {}:latest\n".format(originImage))

    with open("../dependences.txt") as depText:
        text_dep = depText.read()

    otherDep = ''
    if dependencesFile is not None:
        otherDep = dependencesFile

    ########### tuxml/debiantuxml ##########
    dockerFileI.write("ADD linux-4.13.3 /TuxML/linux-4.13.3\n")
    # TODO expand the support of different package manager (like yum, rpm ...)
    dockerFileI.write("ENV TZ=Europe/Paris\n")
    dockerFileI.write("RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone\n")
    dockerFileI.write('RUN apt-get update && apt-get full-upgrade -y && apt-get -qq -y install ' + text_dep + ' ' + otherDep + ' \nRUN wget https://bootstrap.pypa.io/get-pip.py\nRUN python3 get-pip.py\nRUN pip3 install mysqlclient\nRUN pip3 install psutil\nRUN apt-get clean && rm -rf /var/lib/apt/lists/*\nEXPOSE 80\nENV NAME World\n')
    dockerFileI.close()

    strBuildI = 'sudo docker build -t tuxml/{}tuxml:{} .'.format(originImage, tag)
    subprocess.run(strBuildI, shell=True).stdout

    strPushI = 'sudo docker push tuxml/{}tuxml:{}'.format(originImage, tag)
    subprocess.run(strPushI, shell=True).stdout
    ########### tuxml/debiantuxml ##########
    os.chdir('..')

    ########### tuxml/tuxmldebian ##########
    dockerFile = open("Dockerfile", "w")
    dockerFile.write("FROM {}\n".format(newImage))
    dockerFile.write("ENV TZ=Europe/Paris\n")
    dockerFile.write("RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone\n")
    dockerFile.write("RUN apt-get update && apt-get upgrade -y && apt-get full-upgrade -y\n")
    dockerFile.write("ADD core /TuxML\nADD dependences.txt /TuxML\nADD gcc-learn /TuxML/gcc-learn/ \nADD tuxLogs.py /TuxML\nADD runandlog.py /TuxML\nEXPOSE 80\nENV NAME World\nLABEL Description \"Image TuxML\"\n")
    dockerFile.close()
    ########### tuxml/tuxmldebian ##########

# Start of the script

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-v', '--version', help="Use this to choose if you want an image dev or prod (will be delete)")
    parser.add_argument('-b', '--build', help="Image that you want to build, use -f to give the folder where is the TuxML project scripts and a valid dockerfile, default is [.]")
    parser.add_argument('-f', '--folder', help="Folder where is locate a valid docker file use to build a docker image, default is  [.] ", default=".")
    parser.add_argument('-g', '--generate', help="Image use to generate a docker file")
    parser.add_argument('-dep', '--dependences', help="Dependences you want to add to your docker image when you generate your dockerfile")
    parser.add_argument('-p', '--push', help="Push the image on the distant repository")
    parser.add_argument('-t', '--tag', help="Tag of the image you want to generate/build/push",default="prod")
    parser.add_argument('-a', '--all', help="Generate, build, push with default values")

    args = parser.parse_args()

    if args.all:
        linux_dir = os.listdir('./BuildImageInter')
        if "linux-4.13.3" not in linux_dir:
            os.chdir('./BuildImageInter')
            wget = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.13.3.tar.xz"
            subprocess.run(wget, shell=True).stdout
            targz = "tar -xJf linux-4.13.3.tar.xz"
            subprocess.run(targz, shell=True).stdout
        args.generate = args.all
        args.push = args.all
        args.build = args.all

    if args.generate:
        mkGenerate(args)
    if args.build:
        mkBuild(args)
    if args.push:
        mkPush(args)
