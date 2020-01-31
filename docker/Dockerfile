FROM ubuntu:18.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3-pip \
        python3-dev \
        python3-tk \
        locales \
        curl \
    && locale-gen en_US.UTF-8 \
    && update-locale en_US.UTF-8 \
    && export LC_ALL="en_US.UTF-8" \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install \
        shapely \
        matplotlib \
        descartes \
        py2d-fixed \
        dubins

WORKDIR /tmp
RUN cd /tmp \
    && curl -O http://akira.ruc.dk/~keld/research/GLKH/GLKH-1.0.tgz \
    && tar xvfz GLKH-1.0.tgz \
    && cd GLKH-1.0 \
    && make \
    && ln -s /tmp/GLKH-1.0/GLKH /bin

WORKDIR /workspace
RUN ln -s /tmp/GLKH-1.0/LKH /workspace \
    && mkdir TMP

