## Information about the base image
NAME_BASE_IMAGE = "tuxml/minituxml"

# What will be written in the Dockerfile for the base image to produce the image.
CONTENT_BASE_IMAGE = {
    # Constants for the Dockerfile of the "compressed" image
    'DEBIAN_VERSION': 'FROM debian:stretch',
    'LINUX_TAR': "COPY linux-4.13.3.tar.xz linux-4.13.3.tar.xz",
    'TUXML_TAR': "COPY TuxML.tar.xz TuxML.tar.xz", # Not in the base image, prone to change
    'ENV_VARS': ["ENV TZ=Europe/Paris", "ENV DEBIAN_FRONTEND noninteractive"],
    'ZONEINFO': "RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone",
    'RUN_DEP': """RUN apt-get update && apt-get -qq -y install python3 python3-dev python3-pip python3-setuptools 
            default-libmysqlclient-dev apt-file apt-utils && apt-get install -qq -y --no-install-recommends --download-only 
            gcc g++ make binutils util-linux kmod e2fsprogs jfsutils xfsprogs btrfs-progs 
            pcmciautils ppp grub iptables openssl bc reiserfsprogs squashfs-tools quotatool nfs-kernel-server procps mcelog 
            libcrypto++6 git wget qemu-system qemu-utils initramfs-tools lzop liblz4-tool dialog moreutils bison libelf-dev 
            flex libdb5.3-dev""",
    'RUN_PIP': "RUN pip3 install wheel mysqlclient psutil",
    'EXPOSE': "EXPOSE 80",
    'ENV_NAME': "ENV NAME World",
}

## Information about the built image
NAME_IMAGE = "tuxml/tuxmldebian"

# What will be written in the Dockerfile for the compressed docker image.
CONTENT_IMAGE = {
    # Constants for the Dockerfile of the "uncompressed" image
    'PREVIMG_VERSION': "FROM " + NAME_BASE_IMAGE + ":latest",
    'ENV_VARS': ["ENV TZ=Europe/Paris", "ENV DEBIAN_FRONTEND noninteractive"],
    'ZONEINFO': "RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone",
    'LINUX_UNTAR': "RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz",
    'TUXML_UNTAR': "RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz",
    'RUN_DEP_INSTALL': """RUN apt-get install -qq -y --no-install-recommends gcc g++ make binutils util-linux kmod e2fsprogs
                    jfsutils xfsprogs btrfs-progs pcmciautils ppp grub iptables openssl bc reiserfsprogs squashfs-tools quotatool 
                    nfs-kernel-server procps mcelog libcrypto++6 git wget qemu-system qemu-utils initramfs-tools lzop liblz4-tool 
                    dialog moreutils bison libelf-dev flex libdb5.3-dev""",
    'EXPOSE': "EXPOSE 80",
    'ENV_NAME': "ENV NAME World",
}
