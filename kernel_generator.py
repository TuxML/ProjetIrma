#!/usr/bin/python3

"""TuxML entrypoint program

:author: LE MASLE Alexis, PICARD Michaël, DIDOT Gwendal
:version: 2
"""
import argparse
import subprocess
import os
import shutil

__COMPRESSED_IMAGE = "tuxml/tartuxml"
__IMAGE = "tuxml/tuxml"
__DEFAULT_V4 = "4.13.3"
# __sudo_right: internal global variable whose goal is to use sudo if the user
# isn't in the docker group.
__sudo_right = ""


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
    """Set the prompt output color. By default, it reset it to the default
    color.

    :param color: the color to set, defaults to Default, Gray, Black,\
    Red, Ligh_Red, Green, Light_Green, Orange, Light_Orange, Blue,\
    Light_Blue, Purple, Light_Purple 
    :type color: str

    """
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
    """ Ask a confirmation, and return the answer as boolean

    :return: the input confirmation
    :rtype: boolean
    
    """
    answer = input().lower()
    while answer != 'n' and answer != 'y':
        print("y/n")
        answer = input().lower()
    return answer == 'y'


## get_digest_docker_image
# @author PICARD Michaël
# @version 2
# @brief Return the digest of selected docker image
# @param image
# @param tag
def get_digest_docker_image(image, tag=None):
    """Return the digest of selected docker image

    :param image: docker image
    :type image: str
    :param tag: docker tag
    :type tag: str
    :return: digest of selected docker image
    :rtype: int
    """
    cmd = "docker image ls --digests --format {}".format("\"{{.Repository}}")
    if tag is not None:
        image = "{}:{}".format(image, tag)
        cmd = "{}:{}".format(cmd, "{{.Tag}}")
    cmd = "{}{} {} | grep \"{}\"".format(__sudo_right, cmd, "{{.Digest}}\"",
                                         image)
    try:
        result = subprocess.check_output(
            args=cmd,
            shell=True,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as ex:
        raise NotImplementedError("No digest found") from ex
    if len(result) == 0:
        raise NotImplementedError("Image not found.")
    result = result.splitlines()[0].split(" ")
    if result[1] == "<none>":
        raise NotImplementedError("No digest found.")
    return result[1]


## get_id_docker_image
# @author PICARD Michaël
# @version 2
# @brief Return the id of selected docker image
# @param image
# @param tag
def get_id_docker_image(image, tag=None):
    """Return the id of selected docker image

    :param image: docker image
    :type image: str
    :param tag: docker tag
    :type tag: str
    :return: id
    :rtype: string
    """
    cmd = "docker image ls --format {}".format("\"{{.Repository}}")
    if tag is not None:
        image = "{}:{}".format(image, tag)
        cmd = "{}:{}".format(cmd, "{{.Tag}}")
    cmd = "{}{} {} | grep \"{}\"".format(__sudo_right, cmd, "{{.ID}}\"",
                                         image)
    try:
        result = subprocess.check_output(
            args=cmd,
            shell=True,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as ex:
        raise NotImplementedError("No ID found") from ex
    if len(result) == 0:
        raise NotImplementedError("Image not found.")
    result = result.splitlines()[0].split(" ")
    return result[1]


## get_list_image_docker
# @author PICARD Michaël
# @version 1
# @brief Return a list of image corresponding to the given id.
def get_list_image_docker(id_image):
    """Return a list of image corresponding to the given id.

    :param id_image: id of the docker image
    :type id_image: str
    :return: list of image
    :rtype: list
    """
    list_image = list()
    cmd = "docker image ls --format \"{}:{} {}\" | grep {}".format(
        "{{.Repository}}",
        "{{.Tag}}",
        "{{.ID}}",
        id_image
    )
    try:
        result = subprocess.check_output(
            args="{}{}".format(__sudo_right, cmd),
            shell=True,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as ex:
        return list_image
    for line in result.splitlines():
        list_image.append(line.split(" ")[0])
    return list_image


## docker_build
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief build a docker image
# @param image The image name of your choice. Default to None.
# @param tag The tag of your choice. Default to None.
# @param path The path where the Dockerfile is. Default to None, which is
# equivalent to . (current directory).
def docker_build(image=None, tag=None, path=None):
    """Builds a docker image

    :param image: the image name of your choice. Default to None.
    :type image: str
    :param tag: the tag of your choice. Default None.
    :type tag: str
    :param path: path to the dockerfile. Default to None, which is the\
    same as ``.`` (current directory)
    :type path: str
    """    
    if path is None:
        path = "."
    str_build = "docker build".format(image)
    if image is not None:
        str_build = "{} -t {}".format(str_build, image)
        if tag is not None:
            str_build = "{}:{}".format(str_build, tag)
    str_build = "{}{} {}".format(__sudo_right, str_build, path)
    try:
        subprocess.check_call(str_build, shell=True)
    except subprocess.CalledProcessError:
        set_prompt_color("Red")
        print("An error as occured while building the image. Retrying...")
        set_prompt_color()
        subprocess.check_call(str_build, shell=True)


## create_dockerfile
# @author DIDOT Gwendal, PICARD Michaël
# @version 2
# @brief Create and save a Dockerfile
# @param content What you will actually put in your Dockerfile. Default to None.
# @param path Where you want to save your Dockerfile. Default to None, which is
# # equivalent to . (current directory).
def create_dockerfile(content=None, path=None):
    """Create and save a Dockerfile
    
    :param content: dockerfile content
    :type content: str
    :param path: path to the directory to save the dockerfile.\
    Default to None, which is the same as ``.`` (current directory)
    """
    
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
    """Pull a docker image
    
    :param image: docker image to pull
    :type image: str
    :param tag: docker tag. Default to None.
    :type tag: str
    """
    str_pull = "{}docker pull {}".format(__sudo_right, image)
    if tag is not None:
        str_pull = "{}:{}".format(str_pull, tag)
    subprocess.call(args=str_pull, shell=True)


## parser
# @author PICARD Michaël
# @version 1
# @brief Parse the commandline argument
# @return An object where each attribute is one argument and its value.
def parser():
    """Parse the commandline argument

    :return: object in which each attribute is one argument and its\
    value. Check\
    `argparse <https://docs.python.org/3/library/argparse.html>`_\
    for more info.
    :rtype: `argparse.Namespace`_
    
    .. _argparse.Namespace: https://docs.python.org/3.8/library/argparse.html#argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description=""  # TODO: Fill the description
    )
    parser.add_argument(
        "nbcontainer",
        type=int,
        help="Provide the number of container to run. Have to be over 0.",
        nargs='?',
        default=1
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
        "--boot",
        action="store_true",
        help="Optional. Try to boot the kernel after compilation if the compilation "
             "has been successful"
    )
    parser.add_argument(
        "--checksize",
        action="store_true",
        help="Optional. Compute additional size measurements on the kernel and send "
             "the results to the 'sizes' table (can be heavy)."
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
        "--seed",
        help="Give a path to a specific seed options file. These options will be activated before the others are randomly chosen. The file will replace tuxml.config "
    )
    parser.add_argument(
        "--linux_version",
        help="Optional. Give a specific linux version to compile (can be v4 or v5). "
             "Note that its local, will take some time to download the kernel "
             "after compiling, and that the image use to compile it will be "
             "deleted afterward.",
        default=__DEFAULT_V4
    )
    parser.add_argument(
        "--logs",
        help="Optional. Save the logs to the specified path."
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Prevent printing on standard output when compiling. "
             "Will still display the feature warning."
    )
    parser.add_argument(
        "--unit_testing",
        action="store_true",
        help="Optional. Run the unit testing of the compilation script. Prevent"
             " any compilation to happen. Will disable --tiny, --config, "
             "--linux_version, --silent, --fetch_kernel and incremental "
             "feature during runtime."
    )
    parser.add_argument(
        "-n",
        "--number_cpu",
        help="Optional. Specify the number of cpu cores to use while compiling."
             "Useful if your computer can't handle the process at full power.",
        type=int
    )

    return parser.parse_args()


## check_precondition_and_warning
# @author PICARD Michaël
# @version 1
# @brief Check the precondition over commandline argument and warn the user if
# needed.
# @param args The parsed commandline argument.
def check_precondition_and_warning(args):
    """Check the precondition over commandline argument and warn the user
    if needed.

    :param args: parsed command line arguments
    :type args: `argparse.Namespace`_

    .. _args.Namespace: https://docs.python.org/3.8/library/argparse.html#argparse.Namespace
    """ 
    # precondition
    if args.nbcontainer <= 0:
        raise ValueError("You can't run less than 1 container for compilation.")
    if args.incremental < 0:
        raise ValueError("You can't use incremental with negative value.")
    if args.tiny and (args.config is not None):
        raise NotImplementedError(
            "You can't use tiny and config parameter at the same time."
        )
    if args.number_cpu is not None and args.number_cpu <= 0:
        raise NotImplementedError(
            "You can't compile with a negative or null number of cpu."
        )

    if args.unit_testing:
        args.incremental = 0
        args.tiny = None
        args.config = None
        args.silent = None

    # not implemented yet
    if args.incremental > 0:
        raise NotImplementedError(
            "Currently unsupported."
        )

    # warning
    set_prompt_color("Orange")
    # user right : sudo or docker group
    if os.getuid() != 0 and "docker" not in subprocess.check_output(
            "groups",
            shell=True,
            universal_newlines=True):
        global __sudo_right
        __sudo_right = "sudo "
        print("You aren't in the docker group, hence you will be ask superuser"
              " access.")
    if args.dev:
        print("You are using the development version, whose can be unstable.")
    if args.local:
        print("You are using the local version, which means that you could be "
              "out to date, or you could crash if you don't have the image.")
    if args.tiny:
        print("You are using tiny configuration.")
    if args.config is not None:
        print("You are using your specific configuration : {}".format(
            args.config))
    if args.seed is not None:
        print("You are using your specific set of seed options")
    if args.unit_testing:
        print("You will unit test the project, which will not compile any "
              "kernel and could have disabled a few of your option choice.")
    set_prompt_color()


## docker_uncompress_image
# @author PICARD Michaël
# @version 1
# @brief Uncompress the compressed image to create the big one.
def docker_uncompress_image(tag):
    """Uncompress the compressed image to create the big one.

    :param tag: docker tag
    :type tag: str
    """
    content = "FROM {}".format(__COMPRESSED_IMAGE)
    if tag is not None:
        content = "{}:{}".format(content, tag)
    content = "{}\n" \
              "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz\n" \
              "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz\n" \
              "RUN apt-get update && apt-get install -qq -y --no-install-recommends $(cat /dependencies.txt)".format(content)
    create_dockerfile(content=content, path=".")
    docker_build(
        image=__IMAGE,
        tag=tag,
        path="."
    )
    os.remove("./Dockerfile")


## docker_image_update
# @author PICARD Michaël
# @version 4
# @brief Update (if needed) the docker image.
def docker_image_update(tag):
    """Update (if needed) the docker image.

    :param tag: docker tag
    :type tag: str
    :return: either the image has been updated or not
    :rtype: bool
    """
    set_prompt_color("Purple")
    have_been_updated = True
    id_image_base = None
    try:
        print("Trying to update docker image...")
        id_image_base = get_id_docker_image(image=__COMPRESSED_IMAGE, tag=tag)
        before_digest = get_digest_docker_image(image=__COMPRESSED_IMAGE, tag=tag)
        set_prompt_color()
        docker_pull(image=__COMPRESSED_IMAGE, tag=tag)
        after_digest = get_digest_docker_image(image=__COMPRESSED_IMAGE, tag=tag)
        set_prompt_color("Purple")
        if before_digest != after_digest:
            print("Update found, cleaning old image and uncompressing...")
            set_prompt_color()
            docker_image_auto_cleaner(tag, id_image_base)
            docker_uncompress_image(tag)
        elif not docker_image_exist(__IMAGE, tag):
            print("No update but {}:{} doesn't exist. "
                  "Building it...".format(__IMAGE, tag))
            set_prompt_color()
            docker_uncompress_image(tag)
        else:
            print("No update found.")
            have_been_updated = False
    except NotImplementedError:
        set_prompt_color("Red")
        print("An error occured when updating. Cleaning and force update...")
        set_prompt_color()
        if id_image_base is not None:
            docker_image_auto_cleaner(tag, id_image_base)
        docker_pull(image=__COMPRESSED_IMAGE, tag=tag)
        docker_uncompress_image(tag)
    set_prompt_color("Purple")
    print("Updating of docker image done.")
    set_prompt_color()
    return have_been_updated


## docker_image_auto_cleaner
# @author PICARD Michaël
# @version 1
# @brief Will clean all image build with the given tag.
# @details Will throw if a container use the found image.
# ^ this up here is not clear to me (G. Aaron RANDRIANAINA, 26/06/2020)
# @pre An image with a tag containing the tag argument exist.
def docker_image_auto_cleaner(tag, old_image_id=None):
    """Clean all image built with the given tag.

    :pre-condition: An image with the given tag should exist.
    :param tag: docker tag
    :type tag: str
    :param old_image_id: docker image
    :type old_image_id: str
    """
    tag_list = subprocess.check_output(
        args="{}docker image ls {} --format {} | grep {}".format(
            __sudo_right,
            __IMAGE,
            "{{.Tag}}",
            tag
        ),
        shell=True,
        universal_newlines=True
    ).splitlines()
    image_list = ["{}:{}".format(__IMAGE, x) for x in tag_list]
    subprocess.run(
        args="{}docker image rm {}".format(__sudo_right, " ".join(image_list)),
        shell=True,
        check=True
    )

    if old_image_id is not None:
        reference_image_id = list()
        for name in get_list_image_docker(old_image_id):
            if "<none>" not in name:
                reference_image_id.append(name)
        if len(reference_image_id) == 0:
            subprocess.run(
                args="{}docker rmi -f {}".format(__sudo_right, old_image_id),
                shell=True,
                check=True
            )


## replacement of docker_build_v4_image (generalize to any version... of course TuxML was designed for >4.8 version) 
# @author PICARD Michaël, ACHER Mathieu
# @version 1
# @brief It will download and create an image with a different linux v4/v5 inside.
# @details It will build only if it need to. If not, it will just return the
# image tag.
# @pre The __IMAGE:tag image already exist.
# @return The corresponding tag.
def docker_build_version_image(tag, version):
    """Download and create an image with different Linux kernel versions
    inside. Builds only if in need, otherwise return the image tag.

    .. note:: replacement of docker_build_v4_image since `this commit\
    <https://github.com/TuxML/ProjetIrma/commit/b16ac41490fd92548b9a6cb8166447f5f78ffd55>`_\
    (generalize to any version... of course TuxML was designed for\
    >4.8 version)

    :pre-condition: ``__IMAGE:tag`` image exists
    :param tag: docker tag
    :type tag: str
    :param v4: Linux v4 version. If you need 4.14.152, you need to write\
    ``"14.152"``
    :type v4: str
    :return: image's tag
    :rtype: str

    """ 
    tagv = "{}-v{}".format(tag, version)
    if not docker_image_exist(__IMAGE, tagv):
        set_prompt_color("Purple")
        print("Building specific image for linux v{} ...".format(version))
        set_prompt_color()
        linux_kernel = "linux-{}.tar.xz".format(version)
        get_linux_kernel(linux_kernel[:-7])
        docker_file_content = "FROM {0}:{1}\n" \
                              "COPY {2} /TuxML/{2}\n" \
                              "RUN echo \"{3}\" > /kernel_version.txt\n" \
                              "RUN tar xf /TuxML/{2} -C /TuxML && rm /TuxML/{2}\n" \
                              "RUN rm -rf /TuxML/linux-4.13.3".format(
                                  __IMAGE, tag, linux_kernel, version)
        create_dockerfile(docker_file_content)
        docker_build(__IMAGE, tagv)
        os.remove("Dockerfile")
        set_prompt_color("Purple")
        print("Building done.")
        set_prompt_color()
    else:
        set_prompt_color("Purple")
        print("Specific image for linux v{} already exist. "
              "Nothing to do.".format(version))
        set_prompt_color()
    return tagv


##get_linux_kernel
# @author POLES Malo, PICARD Michaël
# @version 3
# @brief Download the linux kernel at the current location
# @param name Specify version of kernel we want. MUST BE A v4.x version or a v5.x version
def get_linux_kernel(name, path=None):
    """Download the Linux kernel in the current directory

    :param name: Linux kernel version.
    :type name: str
    
    .. warning:: Linux kernel version must be v4.xx

    :param path: directory to save the Linux kernel in
    :type path: str
    """
    if path is not None:
        os.chdir(path)
    name += ".tar.xz"
    list_dir = os.listdir('.')
    if name not in list_dir:
        print("Linux kernel not found, downloading", name)
        if name.startswith("linux-4"): 
            wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/{}".format(name)
        elif name.startswith("linux-5"):
            wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v5.x/{}".format(name)
        else:
            print("Unrecognized kernel version (should be 4 or 5)", name)
            return
        subprocess.run(args=wget_cmd, shell=True, check=True)
    else:
        print("Linux kernel found.")


## docker_image_exist
# @author Picard Michaël
# @version 1
# @brief Check the existence of an image.
# @return A boolean value.
def docker_image_exist(image, tag=None):
    """Checks if a docker image really exists

    :param image: docker image to check
    :type image: str
    :param tag: image's tag 
    :type tag: str
    :return: either the docker image exists or not
    :rtype: bool
    """
    cmd = "{}docker image ls -q {}".format(__sudo_right, image)
    if tag is not None:
        cmd = "{}:{}".format(cmd, tag)
    try:
        return len(subprocess.check_output(
            args=cmd,
            shell=True,
            universal_newlines=True,
            stderr=subprocess.DEVNULL
        ).splitlines())
    except subprocess.CalledProcessError:
        return False


def run_docker_compilation(image, incremental, tiny, config, seed,
                           silent, cpu_cores, boot, check_size):
    """Run a docker container to compiler a Linux kernel

    :param image: docker image
    :type image: str
    :param incremental: steps for incremental compilation option
    :type incremental: int
    :param tiny: use Linux tiny configuration
    :type tiny: bool
    :param config: path to a configuration file
    :type config: str
    :param seed:  path to a seed option file
    :type seed: str
    :param silent: verbose option
    :type silent: bool
    :param cpu_cores: number of cpu cores for the compilation
    :type cpu_cores: int
    :param boot: boot the kernel after compilation
    :type boot: bool
    :param check_size: check the size information of the compiled kernel
    :type check_size: bool
    :return: id of the running container
    :rtype: str
    """
    # Starting the container
    container_id = subprocess.check_output(
        args="{}docker run -i -d {}".format(__sudo_right, image),
        shell=True
    ).decode('UTF-8')
    container_id = container_id.split("\n")[0]

    # Converting parameter
    specific_configuration = ""
    if tiny:
        specific_configuration = "--tiny"
    elif config is not None:
        specific_configuration = "--config /TuxML/.config"
        subprocess.call(
            args="{}docker cp {} {}:/TuxML/.config".format(
                __sudo_right, config, container_id),
            shell=True
        )
    elif seed is not None:
        subprocess.call(
            args="{}docker cp {} {}:/TuxML/compilation/tuxml.config".format(
                __sudo_right, seed, container_id),
            shell=True
        )
    if silent:
        silent = "--silent"
    else:
        silent = ""
    if cpu_cores:
        cpu_cores = "--cpu_cores {}".format(cpu_cores)
    else:
        cpu_cores = ""
    if boot:
        boot = "--boot"
    else:
        boot = ""
    if check_size:
        check_size = "--check_size"
    else:
        check_size = ""
    subprocess.call(
        args="{}docker exec -t {} /bin/bash -c '/TuxML/compilation/main.py {} {} {} {} {} {}| ts -s'".format(
            __sudo_right,
            container_id,
            incremental,
            specific_configuration,
            silent,
            cpu_cores,
            boot,
            check_size
        ),
        shell=True
    )
    return container_id


## delete_docker_container
# @author PICARD Michaël
# @version 1
# @brief Stop and delete the container corresponding to the given container_id
def delete_docker_container(container_id):
    """Stop and delete the container corresponding to the given
    container_id

    :param container_id: id of the container
    :type container_id: str
    """
    subprocess.call(
        "{}docker stop {}".format(__sudo_right, container_id), shell=True, stdout=subprocess.DEVNULL)
    subprocess.call(
        "{}docker rm {}".format(__sudo_right, container_id), shell=True, stdout=subprocess.DEVNULL)


def feedback_user(nbcontainer, nbincremental):
    """ Print on standard output a feedback to the user

    :param nbcontainer: number of used containers
    :type nbcontainer: int
    :param nbincremental: number of steps for incremental compilation
    :type nbincremenntal: int
    """
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


def compilation(image, args):
    """Runs the compilation on the specified number of container.

    :param image: docker image
    :type image: str
    :param args: parsed argument options
    :type args: `argparse.Namespace`_
    """
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
            args.seed,
            args.silent,
            args.number_cpu,
            args.boot,
            args.checksize
        )
        if args.logs is not None:
            fetch_logs(container_id, args.logs, args.silent)
        delete_docker_container(container_id)
    if not args.silent:
        feedback_user(args.nbcontainer, args.incremental)


def run_unit_testing(image):
    """Runs unit tests of TuxML on the image

    :param image: docker image
    :type image: str
    """
    # Starting the container
    container_id = subprocess.check_output(
        args="{}docker run -i -d {}".format(__sudo_right, image),
        shell=True
    ).decode('UTF-8')
    container_id = container_id.split("\n")[0]
    print()  # Just visual sugar
    subprocess.call(
        args="{}docker exec -t {} py.test /TuxML/tests "
             "--cov=\"/TuxML/compilation\" -p no:warnings".format(
            __sudo_right, container_id),
        shell=True
    )
    delete_docker_container(container_id)


## fetch_logs
# @author PICARD Michaël
# @version 1
# @brief Fetch all the logs from the container and save them into the directory
def fetch_logs(container_id, directory, silent=False):
    """Fetch all the logs from the container and save them into the
    directory

    :param container_id: id of the container
    :type container_id: str
    :param directory: directory to save the logs in
    :type directory: str
    :param silent: not verbose. Default False
    :type silent: bool
    """
    if not silent:
        print("\nFetching logs from the docker... ", flush=True, end='')
    cmd = "{}docker cp {}:/TuxML/logs {}".format(__sudo_right, container_id,
                                                 directory)
    subprocess.run(args=cmd, shell=True, stdout=subprocess.DEVNULL)
    file_list = os.listdir("{}/logs".format(directory))
    for file in file_list:
        shutil.move(
            os.path.join("{}/logs".format(directory), file),
            os.path.join(directory, file))
    os.rmdir("{}/logs".format(directory))
    if not silent:
        print("Done", flush=True)


if __name__ == "__main__":
    args = parser()
    check_precondition_and_warning(args)

    # Set the image tag to use.
    if args.dev:
        tag = "dev"
    else:
        tag = "prod"

    # Update the image
    have_been_updated = False
    if not args.local:
        have_been_updated = docker_image_update(tag)
    elif not docker_image_exist(__IMAGE, tag):
        set_prompt_color("Red")
        print("The base docker image doesn't exist! Building it...")
        set_prompt_color()
        docker_uncompress_image(tag)

    if args.linux_version != __DEFAULT_V4:
        tag = docker_build_version_image(tag, args.linux_version)

    # Setting image name to run (useful later with linux_version)
    image = "{}:{}".format(__IMAGE, tag)

    if args.unit_testing:
        run_unit_testing(image)
    else:
        compilation(image, args)
