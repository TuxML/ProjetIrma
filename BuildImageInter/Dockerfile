FROM debian:latest
ADD linux-4.13.3 /TuxML/linux-4.13.3
RUN apt-get update && apt-get -qq -y install  
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install mysqlclient
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
EXPOSE 80
ENV NAME World