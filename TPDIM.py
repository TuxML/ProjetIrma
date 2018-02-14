#!/usr/bin/python3

import os
import argparse

# We define the function use in the script


def DockerBuild(image, *location):
    print("Update of the docker image")
    # Build the choosen docker image
    if location in args:
        strBuild = 'sudo docker build -t {} {}'.format(image, location)
        print(strBuild)
        pass
    else:
        strBuild = 'sudo docker build -t tuxml/tuxml{} .'.format(image)
    os.system(strBuild)


def DockerPush(repository):
    print("Push of the image on the distant repository")
    # Push of the docker image on docker hub
    strpush = 'sudo docker push tuxml/tuxml{}'.format(repository)
    rstrpush = os.system(strpush)
    # If needed, login to the repository
    if rstrpush == 256:
        print("You need to login on Docker hub")
        str3 = 'sudo docker login'
        os.system(str3)


def DockerGenerate(originImage, *dependencesFile):
    newImage = 'tuxml/{}tuxml:prod'.format(originImage)
    os.chdir('BuildImageInter')
    # strPres = 'sudo docker search tuxml | grep {}tuxml > present.txt'.format(originImage)
    # os.system(strPres)
    # presentText = open("present.txt", "r")
    # res = presentText.readline()
    # if not res:
    dockerFileI = open("Dockerfile", "w")
    if dependencesFile in args:
        dep = open(dependencesFile, "r")
        for i in len(dep):
            
            pass
    dockerFileI.write("FROM {}:latest\n".format(originImage))
    dockerFileI.write("ADD linux-4.13.3 /TuxML/linux-4.13.3\nRUN apt-get update\nRUN apt-get -qq -y install python3 apt-file apt-utils gcc make binutils util-linux kmod e2fsprogs jfsutils xfsprogs btrfs-progs pcmciautils ppp grub iptables openssl bc reiserfsprogs squashfs-tools quotatool nfs-kernel-server procps mcelog libcrypto++6 python3-dev default-libmysqlclient-dev git wget\nRUN wget https://bootstrap.pypa.io/get-pip.py\nRUN python3 get-pip.py\nRUN pip3 install mysqlclient\nRUN apt-get clean && rm -rf /var/lib/apt/lists/*\nEXPOSE 80\nENV NAME World")
    dockerFileI.close()
    strBuildI = 'sudo docker build -t tuxml/{}tuxml:prod .'.format(originImage)
    os.system(strBuildI)
    strPushI = 'sudo docker push tuxml/{}tuxml:prod'.format(originImage)
    os.system(strPushI)
    # else:
    # print("tuxml/{}tuxml:prod already exist".format(originImage))
    os.chdir('..')
    dockerFile = open("Dockerfile", "w")
    dockerFile.write("FROM {}\n".format(newImage))
    dockerFile.write("ADD core /TuxML\nADD tuxLogs.py /TuxML\nEXPOSE 80\nENV NAME World\nLABEL Description \"Image TuxML\"\n")
    dockerFile.close()


# Start of the script


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="test", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-b', '--build', help="Image that you want to build, use -f to give the folder where is the TuxML project scripts and a valid dockerfile, default is [.]")
    parser.add_argument('-f', '--folder', help="Folder where is locate a valid docker file use to build a docker image, default is  [.] ", default=".")
    parser.add_argument('-g', '--generate', help="Image use to generate a docker file")
    parser.add_argument('-dep', '--dependences', help="Dependences you want to add to your docker image when you generate your dockerfile")
    parser.add_argument('-p', '--push', help="Push the image on the distant repository")

args = parser.parse_args()

if args.generate:
    DocPre = os.listdir('.')
    if "Dockerfile" in DocPre:
        print("It seems that a DockerFile already exist, please move it away or I'll be delete by the generation, do wish to continue ? (y/n)")
        rep = input()
        rep.lower()
        if rep == "y":
            if args.dependences:
                DockerGenerate(args.generate, args.dependences)
            else:
                DockerGenerate(args.generate)
        else:
            print("Canceled")
            exit(0)

if args.push:
    DockerPush(args.push)
if args.build:
    if args.folder:
        DocPre = os.listdir(args.folder)
        if "Dockerfile" not in DocPre:
            print("Please give a folder with a valid Dockerfile")
            exit(-1)
        else:
            DockerBuild(args.build, args.folder)
    else:
        DockerBuild(args.image)
