FROM tuxml/debiantuxml:dev
RUN tar xf /TuxML/linux-4.13.3.tar.xz -C /TuxML && rm /TuxML/linux-4.13.3.tar.xz
RUN tar xf /TuxML/TuxML.tar.xz -C /TuxML && rm /TuxML/TuxML.tar.xz
RUN apt-get install -qq -y --no-install-recommends $(cat /dependencies.txt)
EXPOSE 80
ENV NAME World