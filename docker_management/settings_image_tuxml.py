LINUX_KERNEL = 'linux-4.13.3'

## Information about the base image
NAME_BASE_IMAGE = "tuxml/basetuxml"

BASIC_DEP = "gcc g++ make binutils util-linux kmod e2fsprogs jfsutils xfsprogs btrfs-progs pcmciautils ppp grub iptables openssl bc reiserfsprogs squashfs-tools quotatool nfs-kernel-server procps mcelog libcrypto++6 git wget qemu-system qemu-utils initramfs-tools lzop liblz4-tool dialog moreutils bison libelf-dev flex libdb5.3-dev qemu"

# What will be written in the Dockerfile for the base image to produce the image.
CONTENT_BASE_IMAGE = {
    # Constants for the Dockerfile of the "compressed" image
    'DEBIAN_VERSION': 'FROM debian:stretch',
    'MKDIR_TUXML': "RUN mkdir /TuxML",
    'LINUX_TAR': "COPY linux-4.13.3.tar.xz /TuxML/linux-4.13.3.tar.xz",
    'ENV_VARS': "ENV TZ=Europe/Paris\nENV DEBIAN_FRONTEND noninteractive",
    'ZONEINFO': "RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone",
    'RUN_DEP': "RUN apt-get update && apt-get -qq -y install python3 python3-dev python3-pip python3-setuptools default-libmysqlclient-dev apt-file apt-utils && apt-get install -qq -y --no-install-recommends --download-only " +
            BASIC_DEP,
    'RUN_DEP_FILE': "RUN echo " + BASIC_DEP + " > /dependencies.txt",
    'RUN_PIP': "RUN pip3 install wheel mysqlclient psutil pytest pytest-cov",
    'CPRUN_BB': "COPY installBusyBox.sh /installBusyBox.sh\n"
                "COPY init /init\n"
                "RUN chmod 777 /installBusyBox.sh\n"
                "RUN ./installBusyBox.sh\n"
                "RUN rm installBusyBox.sh",
    'EXPOSE': "EXPOSE 80",
    'ENV_NAME': "ENV NAME World",
}

## Information about the built image
NAME_IMAGE = "tuxml/tartuxml"

# What will be written in the Dockerfile for the compressed docker image.
CONTENT_IMAGE = {
    # Constants for the Dockerfile of the "uncompressed" image
    'PREVIMG_VERSION': "FROM " + NAME_BASE_IMAGE,
    'TUXML_TAR': "COPY TuxML.tar.xz /TuxML/TuxML.tar.xz",
    'RUN_DEP': "",
    'RUN_DEP_FILE': "",
    'EXPOSE': "EXPOSE 80",
    'ENV_NAME': "ENV NAME World",
}


NAME_BIG_IMAGE = "tuxml/tuxml"
CONTENT_BIG_IMAGE = {
    'PREVIMG_VERSION': "FROM " + NAME_IMAGE,
    'LINUX_UNTAR': "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz",
    'TUXML_UNTAR': "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz",
    'RUN_DEP_FILE': "RUN apt-get install -qq -y --no-install-recommends $(cat /dependencies.txt)",
    'EXPOSE': "EXPOSE 80",
    'ENV_NAME': "ENV NAME World",
}
