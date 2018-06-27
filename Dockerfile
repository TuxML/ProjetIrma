FROM tuxml/debiantuxml:dev
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get upgrade -y && apt-get full-upgrade -y
ADD core /TuxML
ADD dependences.txt /TuxML
ADD core-correlation /TuxML/core-correlation/ 
ADD tuxLogs.py /TuxML
ADD runandlog.py /TuxML
EXPOSE 80
ENV NAME World
LABEL Description "Image TuxML"
