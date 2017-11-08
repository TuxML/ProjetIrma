FROM tuxml/debiantuxml:latest

ADD . /TuxML

EXPOSE 80

ENV NAME World

LABEL Description "Image TUXML"
RUN apt-get update
RUN apt-get -qq -y install gcc make binutils util-linux kmod e2fsprogs jfsutils xfsprogs btrfs-progs pcmciautils ppp grub iptables openssl bc
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
