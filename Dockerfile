FROM tuxml/debiantuxml:dev
RUN apt-get update && apt-get full-upgrade -y
ADD core /TuxML
ADD gcc-learn /TuxML/gcc-learn/ 
ADD tuxLogs.py /TuxML
ADD runandlog.py /TuxML
EXPOSE 80
ENV NAME World
LABEL Description "Image TuxML"
