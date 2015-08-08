FROM ubuntu:latest
RUN apt-get update && apt-get update -y

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
RUN locale-gen en_US en_US.UTF-8
RUN dpkg-reconfigure locales

RUN apt-get install -y python3-pip uwsgi uwsgi-plugin-python3
RUN pip3 install virtualenv

RUN useradd -d /opt/level2 -m level2

WORKDIR /opt/level2

COPY . /opt/level2/

USER level2
ENV HOME /opt/level2
ENV USER level2

RUN /opt/level2/build.sh

CMD /opt/level2/run.sh

EXPOSE 3031
