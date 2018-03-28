FROM tuxml/debiantuxml:dev
ADD core /TuxML
ADD gcc-learn/ExecConfig.py /TuxML/gcc-learn/ExecConfig.py 
ADD gcc-learn/ConfigFile /TuxML/gcc-learn/ 
ADD tuxLogs.py /TuxML
EXPOSE 80
ENV NAME World
LABEL Description "Image TuxML"
