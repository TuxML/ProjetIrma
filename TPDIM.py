#!/usr/bin/python3

## @file TPDIM.py
# @author DIDOT Gwendal ACHER Mathieu
# @copyright Apache License 2.0
# @brief Script use to simplified the creation and use of Docker image.
# @details This script was design to help member of the TuxML project to easily use Docker, without any knowledge require
#  other than what a Docker image is (check https://docs.docker.com/get-started/ for more information).

# Use 'TPDIM -h' to have more information about the options of the script

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


## mkGenerate
#  @author ACHER Mathieu
# @param args The list of arguments give to the script
def mkGenerate(args):
    DocPre = os.listdir('.')
    if "Dockerfile" in DocPre: # We check if the dockerfile already exist and let the choice to the user to keep it or te generate a new one.
        print("It seems that a DockerFile already exist, please move it away or it'll be delete by the generation, do you wish to continue ? (y/n)")
        rep = input()
        rep.lower()
        if rep == "y":
            if args.dependences: # If the user give to the script a different dependeces file than the default one, we use it instead
                depText = args.dependences
                openDep = open(depText)
                strDep = openDep.read()
                DockerGenerate(args.generate, args.tag, strDep)
            else:
                DockerGenerate(args.generate, args.tag)
        else:
            print("Canceled")
            exit(-1)


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
            DockerBuild(args.build, args.tag, args.folder)
    else:
        DockerBuild(args.image, args.tag)


## mkPush
#  @author ACHER Mathieu
# @param args The list of arguments give to the script
def mkPush(args):
    DockerPush(args.push, args.tag)


def DockerBuild(image, tag, *location):
    print("Update of the docker image")
    # Build the choosen docker image
    if location in args:
        strBuild = 'sudo docker build -t tuxml/tuxml{}:{} {}'.format(image, tag, location)
        print(strBuild)
        pass
    else:
        strBuild = 'sudo docker build -t tuxml/tuxml{}:{} .'.format(image, tag)
    os.system(strBuild)


def DockerPush(repository, tag):
    print("Push of the image on the distant repository")
    # Push of the docker image on docker hub
    strpush = 'sudo docker push tuxml/tuxml{}:{}'.format(repository, tag)
    rstrpush = os.system(strpush)
    # If needed, login to the repository
    if rstrpush == 256:
        print("You need to login on Docker hub")
        str3 = 'sudo docker login'
        os.system(str3)
        DockerPush(repository, tag)


## TODO: we need to split the method in two (one for dependencies; the other for updating TUXML)
def DockerGenerate(originImage, tag, *dependencesFile):
    newImage = 'tuxml/{}tuxml:{}'.format(originImage, tag)
    os.chdir('BuildImageInter')
    dockerFileI = open("Dockerfile", "w")
    dockerFileI.write("FROM {}:latest\n".format(originImage))
    depText = open("../dependences.txt", 'r') ### TODO; Change to let user choose what dependences file they want to use
    text_dep = depText.read()
    dockerFileI.write("ADD linux-4.13.3 /TuxML/linux-4.13.3\n")
    dockerFileI.write("RUN apt-get update && apt-get -qq -y install " + text_dep + " \nRUN wget https://bootstrap.pypa.io/get-pip.py\nRUN python3 get-pip.py\nRUN pip3 install mysqlclient\nRUN pip3 install psutil\nRUN apt-get clean && rm -rf /var/lib/apt/lists/*\nEXPOSE 80\nENV NAME World\n")
    dockerFileI.close()
    strBuildI = 'sudo docker build -t tuxml/{}tuxml:{} .'.format(originImage, tag)
    os.system(strBuildI)
    strPushI = 'sudo docker push tuxml/{}tuxml:{}'.format(originImage, tag)
    os.system(strPushI)
    os.chdir('..')
    dockerFile = open("Dockerfile", "w")
    dockerFile.write("FROM {}\n".format(newImage))
    # dockerFile.write("ADD core /TuxML\nADD gcc-learn/ExecConfig.py /TuxML/gcc-learn/ExecConfig.py \nADD gcc-learn/ConfigFile /TuxML/gcc-learn/ \nADD tuxLogs.py /TuxML\nEXPOSE 80\nENV NAME World\nLABEL Description \"Image TuxML\"\n")
    dockerFile.write("ADD core /TuxML\nADD gcc-learn /TuxML/gcc-learn/ \nADD tuxLogs.py /TuxML\nADD runandlog.py /TuxML\nEXPOSE 80\nENV NAME World\nLABEL Description \"Image TuxML\"\n")
    dockerFile.close()


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
        os.getcwd()
        wget = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.13.3.tar.xz"
        os.system(wget)
        targz = "tar -xJf linux-4.13.3.tar.xz" ### TODO; use subprocess instead
        os.system(targz)
        pass
    args.generate = args.all
    args.push = args.all
    args.build = args.all

if args.generate:
    mkGenerate(args)
if args.build:
    mkBuild(args)
if args.push:
    mkPush(args)
