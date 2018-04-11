FROM tuxml/debiantuxml:dev
ADD core /TuxML
ADD gcc-learn /TuxML/gcc-learn/ 
ADD tuxLogs.py /TuxML
ADD runandlog.py /TuxML
EXPOSE 80
ENV NAME World
LABEL Description "Image TuxML"
