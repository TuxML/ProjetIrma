FROM tuxml/debiantuxml:latest

ADD . /TuxML

EXPOSE 80

ENV NAME World

LABEL Description "Image TUXML"
