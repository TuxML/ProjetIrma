#!/usr/bin/python3

import os
import argparse

# We define the function use in the script


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


def DockerGenerate(originImage, tag, *dependencesFile):
    newImage = 'tuxml/{}tuxml:{}'.format(originImage, tag)
    os.chdir('BuildImageInter')
    dockerFileI = open("Dockerfile", "w")
    dockerFileI.write("FROM {}:latest\n".format(originImage))
    depText = ""
    if len(dependencesFile) != 0:
        depText = dependencesFile[0]
    dockerFileI.write("ADD linux-4.13.3 /TuxML/linux-4.13.3\nRUN apt-get update && apt-get -qq -y install " + depText + " \nRUN wget https://bootstrap.pypa.io/get-pip.py\nRUN python3 get-pip.py\nRUN pip3 install mysqlclient\nRUN apt-get clean && rm -rf /var/lib/apt/lists/*\nEXPOSE 80\nENV NAME World")
    dockerFileI.close()
    strBuildI = 'sudo docker build -t tuxml/{}tuxml:{} .'.format(originImage, tag)
    os.system(strBuildI)
    strPushI = 'sudo docker push tuxml/{}tuxml:{}'.format(originImage, tag)
    os.system(strPushI)
    os.chdir('..')
    dockerFile = open("Dockerfile", "w")
    dockerFile.write("FROM {}\n".format(newImage))
    dockerFile.write("ADD core /TuxML\nADD gcc-learn/ExecConfig.py /TuxML/gcc-learn/ExecConfig.py \nADD gcc-learn/ConfigFile /TuxML/gcc-learn/ \nADD tuxLogs.py /TuxML\nEXPOSE 80\nENV NAME World\nLABEL Description \"Image TuxML\"\n")
    dockerFile.close()


# Start of the script


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="test", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-v', '--version', help="Use this to choose if you want an image dev or prod (will be delete)")
    parser.add_argument('-b', '--build', help="Image that you want to build, use -f to give the folder where is the TuxML project scripts and a valid dockerfile, default is [.]")
    parser.add_argument('-f', '--folder', help="Folder where is locate a valid docker file use to build a docker image, default is  [.] ", default=".")
    parser.add_argument('-g', '--generate', help="Image use to generate a docker file")
    parser.add_argument('-dep', '--dependences', help="Dependences you want to add to your docker image when you generate your dockerfile")
    parser.add_argument('-p', '--push', help="Push the image on the distant repository")
    parser.add_argument('-t', '--tag', help="Tag of the image you want to generate/build/push")

args = parser.parse_args()

if args.generate:
    DocPre = os.listdir('.')
    if "Dockerfile" in DocPre:
        print("It seems that a DockerFile already exist, please move it away or I'll be delete by the generation, do wish to continue ? (y/n)")
        rep = input()
        rep.lower()
        if rep == "y":
            if args.dependences:
                depText = args.dependences
                openDep = open(depText)
                strDep = openDep.read()
                DockerGenerate(args.generate, args.tag, strDep)
            else:
                DockerGenerate(args.generate, args.tag)
        else:
            print("Canceled")
            exit(0)

if args.push:
    DockerPush(args.push, args.tag)
if args.build:
    if args.folder:
        DocPre = os.listdir(args.folder)
        if "Dockerfile" not in DocPre:
            print("Please give a folder with a vdevalid Dockerfile")
            exit(-1)
        else:
            DockerBuild(args.build, args.tag, args.folder)
    else:
        DockerBuild(args.image, args.tag)
