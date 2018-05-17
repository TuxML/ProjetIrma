FROM debian:latest
ADD linux-4.13.3 /TuxML/linux-4.13.3
RUN apt-get update && apt-get -qq -y install python3 apt-file apt-utils gcc make binutils util-linux kmod e2fsprogs jfsutils xfsprogs btrfs-progs pcmciautils ppp grub iptables openssl bc reiserfsprogs squashfs-tools quotatool nfs-kernel-server procps mcelog libcrypto++6 python3-dev default-libmysqlclient-dev git wget qemu-system qemu-utils initramfs-tools
 
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install mysqlclient
RUN pip3 install psutil
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
EXPOSE 80
ENV NAME World
