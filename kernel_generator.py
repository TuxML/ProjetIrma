#!/usr/bin/python3

## @file kernel_generator.py
# @author LE MASLE Alexis, PICARD Michaël
# @version 2

import argparse
import subprocess
import os

_COMPRESSED_IMAGE = "tuxml/debiantuxml"
_IMAGE = "tuxml/tuxmldebian"

## set_prompt_color
# @author PICARD Michaël
# @version 1
# @brief Set the prompt output color. By default, it reset it to the default
# color.
# @param color The color to set. It can be:
# - Default
# - Gray
# - Black
# - Red
# - Light_Red
# - Green
# - Light_Green
# - Orange
# - Light_Orange
# - Blue
# - Light_Blue
# - Purple
# - Light_Purple
def set_prompt_color(color="Default"):
    colors = {
        "Default": "\033[0m",  # Default color
        "Gray": "\033[38;5;7m",  # Debug
        "Black": "\033[38;5;16m",
        "Red": "\033[38;5;1m",  # Errors messages
        "Light_Red": "\033[38;5;9m",
        "Green": "\033[38;5;2m",  # Success messages
        "Light_Green": "\033[38;5;10m",
        "Orange": "\033[38;5;3m",  # Warning
        "Light_Orange": "\033[38;5;11m",
        "Blue": "\033[38;5;4m",
        "Light_Blue": "\033[38;5;12m",  # Informations
        "Purple": "\033[38;5;5m",
        "Light_Purple": "\033[38;5;13m"  # Informations
        # BLUE_2 = "\033[38;5;6m"
        # LIGHT_BLUE_2 = "\033[38;5;14m"
    }
    try:
        print(colors[color], end='')
    except KeyError:
        raise KeyError("Unknown color.")


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


## get_digest_docker_image
# @author PICARD Michaël
# @version 1
# @brief Return the digest of selected docker image
# @param image
# @param tag
def get_digest_docker_image(image, tag=None):
    if tag is not None:
        image = "{}:{}".format(image, tag)
    cmd = "docker image ls {} --format {{.Digest}}".format(image)
    result = subprocess.check_output(
        args=cmd,
        shell=True
    )
    result = result.decode('UTF-8')
    result = result.splitlines()
    if len(result) == 0:
        raise NotImplementedError("Image not found.")
    if result[0] == "<none>":
        raise NotImplementedError("No digest found.")
    return result[0]


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
    subprocess.call(str_build, shell=True)


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


## docker_pull
# @author PICARD Michaël
# @version 1
# @brief pull a docker image
# @param image The image name that you want to pull.
# @param tag The tag's image. Default to None.
def docker_pull(image, tag=None):
    str_pull = "sudo docker pull {}".format(image)
    if tag is not None:
        str_pull = "{}:{}".format(image, tag)
    print("commande : {}".format(str_pull))
    subprocess.call(args=str_pull, shell=True)


## parser
# @author PICARD Michaël
# @version 1
# @brief Parse the commandline argument
# @return An object where each attribute is one argument and its value.
def parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "nbcontainer",
        type=int,
        help="Provide the number of container to run. Have to be over 0."
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Use the image with dev tag instead of prod's one."
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Don't try update the image to run, i.e. use the local version."
    )
    return parser.parse_args()


## check_precondition_and_warning
# @author PICARD Michaël
# @version 1
# @brief Check the precondition over commandline argument and warn the user if
# needed.
# @param args The parsed commandline argument.
def check_precondition_and_warning(args):
    if args.nbcontainer <= 0:
        raise ValueError("You can't run less than 1 compilation.")
    if args.dev:
        set_prompt_color("Orange")
        print("You are using the development version, whose can be unstable.")
        set_prompt_color()
    if args.local:
        set_prompt_color("Orange")
        print("You are using the local version, which means that you could be "
              "out to date, or you could crash if you don't have the image.")
        set_prompt_color()


## docker_uncompress_image
# @author PICARD Michaël
# @version 1
# @brief Uncompress the compressed image to create the big one.
def docker_uncompress_image():
    content = "FROM {}".format(_COMPRESSED_IMAGE)
    if tag is not None:
        content = "{}:{}".format(content, tag)
    content = "{}\n" \
              "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz\n" \
              "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz\n" \
              "RUN apt-get install -qq -y --no-install-recommends $(cat /dependencies.txt)\n" \
              "EXPOSE 80\n" \
              "ENV NAME World".format(content)
    create_dockerfile(content=content, path=".")
    docker_build(
        image=_IMAGE,
        tag=tag,
        path="."
    )


## docker_image_update
# @author PICARD Michaël
# @version 1
# @brief Update (if needed) the docker image.
def docker_image_update(tag):
    try:
        before_digest = get_digest_docker_image(image=_COMPRESSED_IMAGE, tag=tag)
        docker_pull(image=_COMPRESSED_IMAGE, tag=tag)
        after_digest = get_digest_docker_image(image=_COMPRESSED_IMAGE, tag=tag)
        if before_digest != after_digest:
            docker_uncompress_image()
    except NotImplementedError:
        docker_pull(image=_COMPRESSED_IMAGE, tag=tag)
        docker_uncompress_image()


def run_docker_compilation(tag, incremental):
    container_id = subprocess.check_output(
        args="sudo docker run -i -d {}:{}".format(_IMAGE, tag),
        shell=True
    ).decode('UTF-8')
    container_id = container_id.split("\n")[0]
    subprocess.run(
        args="sudo docker exec -t {} /TuxML/runandlog.py {}".format(
            container_id,
            incremental),
        shell=True
    )
    return container_id


## delete_docker_container
# @author PICARD Michaël
# @version 1
# @brief Stop and delete the container corresponding to the given container_id
def delete_docker_container(container_id):
    subprocess.call(
        "sudo docker stop {}".format(container_id), shell=True, stdout=subprocess.DEVNULL)
    subprocess.call(
        "sudo docker rm {}".format(container_id), shell=True, stdout=subprocess.DEVNULL)


def feedback_user(nbcontainer, nbincremental):
    total_of_compilation = nbcontainer * (nbincremental + 1)

    set_prompt_color("Light_Blue")
    print("\nYour tamago... database Irma_db ate ", end="")
    set_prompt_color("Green")
    print(total_of_compilation, end="")
    set_prompt_color("Light_Blue")
    print(" compilations data, come back later to feed it!")

    print("Total number of container used : ", end="")
    set_prompt_color("Green")
    print(nbcontainer)

    set_prompt_color("Light_Blue")
    print("Number of compilations in a container : ", end="")
    set_prompt_color("Green")
    print(nbincremental + 1, end="")
    set_prompt_color("Light_Blue")
    print(" ( 1 basic compilation + ", end="")
    set_prompt_color("Green")
    print(nbincremental, end="")
    set_prompt_color("Light_Blue")
    print(" incremental compilations).")

    set_prompt_color("Light_Blue")
    print("Total number of compilations : ", end="")
    set_prompt_color("Green")
    print(total_of_compilation)
    set_prompt_color()


if __name__ == "__main__":
    args = parser()
    check_precondition_and_warning(args)

    # Set the image tag to use.
    if args.dev:
        tag = "dev"
    else:
        tag = "prod"

    if not args.local:
        docker_image_update(tag)
    for i in range(args.nbcontainer):
        set_prompt_color("Light_Blue")
        print("\n=============== Docker number ", i, " ===============", end='')
        set_prompt_color()
        print('\n', end='')

        container_id = run_docker_compilation(tag, 0)
        delete_docker_container(container_id)

    feedback_user(args.nbcontainer, 0)
