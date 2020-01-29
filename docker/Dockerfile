FROM ubuntu:18.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3-pip \
        python3-dev \
        python3-tk \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install \
        shapely \
        matplotlib \
        descartes \
        py2d-fixed
