#!/usr/bin/python3

## @file kernel_generator.py
# @author LE MASLE Alexis, PICARD Michaël
# @version 2

import argparse
import subprocess
import os

_COMPRESSED_IMAGE = "tuxml/tartuxml"
_IMAGE = "tuxml/tuxml"


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
        print(colors[color], end='', flush=True)
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
    cmd = "docker image ls --format {}".format("\"{{.Repository}}")
    if tag is not None:
        image = "{}:{}".format(image, tag)
        cmd = "{}:{}".format(cmd, "{{.Tag}}")
    cmd = "{} {} | grep \"{}\"".format(cmd, "{{.Digest}}\"", image)
    try:
        result = subprocess.check_output(
            args=cmd,
            shell=True,
        )
    except subprocess.CalledProcessError as ex:
        raise NotImplementedError("No digest found") from ex
    result = result.decode('UTF-8')
    result = result.splitlines()
    if len(result) == 0:
        raise NotImplementedError("Image not found.")
    result = result[0].split(" ")
    if result[1] == "<none>":
        raise NotImplementedError("No digest found.")
    return result[1]


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
    str_pull = "docker pull {}".format(image)
    if tag is not None:
        str_pull = "{}:{}".format(str_pull, tag)
    subprocess.call(args=str_pull, shell=True)


## parser
# @author PICARD Michaël
# @version 1
# @brief Parse the commandline argument
# @return An object where each attribute is one argument and its value.
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "nbcontainer",
        type=int,
        help="Provide the number of container to run. Have to be over 0."
    )
    parser.add_argument(
        "incremental",
        type=int,
        help="Optional. Provide the number of additional incremental "
             "compilation. Have to be 0 or over.",
        nargs='?',
        default=0
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
    parser.add_argument(
        "--tiny",
        action="store_true",
        help="Use Linux tiny configuration. Incompatible with --config "
             "argument."
    )
    parser.add_argument(
        "--config",
        help="Give a path to specific configuration file. Incompatible with "
             "--tiny argument."
    )
    parser.add_argument(
        "--linux4_version",
        help="Optional. Give a specific linux4 version to compile. "
             "Note that its local, will take some time to download the kernel "
             "after compiling, and that the image use to compile it will be "
             "deleted afterward.",
    )
    parser.add_argument(
        "--logs",
        help="Optional. Save the logs to the specified path."
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Prevent printing on standard output when compiling."
    )
    parser.add_argument(
        "--fetch_kernel",
        help="Optional. Fetch linux kernel from the docker container."
    )
    parser.add_argument(
        "--unit_testing",
        action="store_true",
        help="Optional. Run the unit testing of the compilation script. Prevent"
             " any compilation to happen. Will disable --tiny, --config, "
             "--linux4_version, --silent, --fetch_kernel and incremental "
             "feature during runtime."
    )

    return parser.parse_args()


## check_precondition_and_warning
# @author PICARD Michaël
# @version 1
# @brief Check the precondition over commandline argument and warn the user if
# needed.
# @param args The parsed commandline argument.
def check_precondition_and_warning(args):
    # precondition
    if args.nbcontainer <= 0:
        raise ValueError("You can't run less than 1 container for compilation.")
    if args.incremental < 0:
        raise ValueError("You can't use incremental with negative value.")
    if args.tiny and (args.config is not None):
        raise NotImplementedError(
            "You can't use tiny and config parameter at the same time."
        )
    if args.unit_testing:
        args.incremental = 0
        args.tiny = None
        args.config = None
        args.linux4_version = None
        args.fetch_kernel = None
        args.silent = None

    # not implemented yet
    if args.config is not None \
            or args.linux4_version is not None \
            or args.logs is not None \
            or args.fetch_kernel is not None \
            or args.unit_testing:
        raise NotImplementedError(
            "Currently unsupported."
        )


    # warning
    set_prompt_color("Orange")
    if args.dev:
        print("You are using the development version, whose can be unstable.")
    if args.local:
        print("You are using the local version, which means that you could be "
              "out to date, or you could crash if you don't have the image.")
    if args.tiny:
        print("You are using tiny configuration.")
    if args.config is not None:
        print("You are using your specific configuration.")
    if args.fetch_kernel is not None:
        print("You will retrieve the kernel after the compilation phase, if it"
              " succeed.")
    if args.unit_testing is not None:
        print("You will unit test the project, which will not compile any "
              "kernel and could have disabled a few of your option choice.")
    if args.silent:
        print("You have enable the silent mode.")
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
    set_prompt_color("Purple")
    try:
        print("Trying to update docker image...")
        before_digest = get_digest_docker_image(image=_COMPRESSED_IMAGE, tag=tag)
        docker_pull(image=_COMPRESSED_IMAGE, tag=tag)
        after_digest = get_digest_docker_image(image=_COMPRESSED_IMAGE, tag=tag)
        if before_digest != after_digest:
            print("Update found, uncompressing...")
            docker_uncompress_image()
        else:
            print("No update found.")
    except NotImplementedError:
        set_prompt_color("Red")
        print("An error occured when updating. Force update...")
        set_prompt_color()
        docker_pull(image=_COMPRESSED_IMAGE, tag=tag)
        docker_uncompress_image()
    set_prompt_color("Purple")
    print("Updating of docker image done.")
    set_prompt_color()


def run_docker_compilation(image, incremental, tiny, config, silent):
    # Starting the container
    container_id = subprocess.check_output(
        args="docker run -i -d {}".format(image),
        shell=True
    ).decode('UTF-8')
    container_id = container_id.split("\n")[0]

    # Converting parameter
    specific_configuration = ""
    if tiny:
        specific_configuration = "--tiny"
    elif config is not None:
        specific_configuration = "--path /TuxML/.config"
        subprocess.call(
            args="docker cp {} {}:/TuxML/.config".format(container_id, config),
            shell=True
        )
    if silent:
        silent = "--silent"
    else:
        silent = ""

    subprocess.call(
        args="docker exec -t {} /TuxML/runandlog.py {} {} {}".format(
            container_id,
            incremental,
            specific_configuration,
            silent
        ),
        shell=True
    )
    return container_id


## delete_docker_container
# @author PICARD Michaël
# @version 1
# @brief Stop and delete the container corresponding to the given container_id
def delete_docker_container(container_id):
    subprocess.call(
        "docker stop {}".format(container_id), shell=True, stdout=subprocess.DEVNULL)
    subprocess.call(
        "docker rm {}".format(container_id), shell=True, stdout=subprocess.DEVNULL)


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

    # Update the image
    if not args.local:
        docker_image_update(tag)

    # Setting image name to run (useful later with linux4_version)
    image = "{}:{}".format(_IMAGE, tag)

    for i in range(args.nbcontainer):
        if not args.silent:
            set_prompt_color("Light_Blue")
            print("\n=============== Docker number ", i, " ===============")
            set_prompt_color()

        container_id = run_docker_compilation(
            image,
            args.incremental,
            args.tiny,
            args.config,
            args.silent
        )
        delete_docker_container(container_id)

    feedback_user(args.nbcontainer, args.incremental)
