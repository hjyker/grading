FROM ubuntu:20.04

ENV LANG C.UTF-8
ENV PATH="/code:${PATH}"
ENV PYTHONPATH="/code:${PYTHONPATH}"

RUN sed -i "s/archive.ubuntu.com/mirrors.aliyun.com/g" /etc/apt/sources.list \
  && sed -i '/security.ubuntu.com/d' /etc/apt/sources.list \
  && apt update \
  && apt -y upgrade \
  && apt install -y --no-install-recommends \
    vim curl uuid-dev \
    python3-pip python3-dev default-libmysqlclient-dev build-essential \
    iputils-ping net-tools netcat git \
  && DEBIAN_FRONTEND=noninteractive apt install -y tzdata \
  && apt autoclean \
  && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure --frontend noninteractive tzdata

SHELL [ "/bin/bash", "-c"]
RUN ln -s $(which python3) /usr/bin/python
RUN mkdir -p ~/.pip
RUN echo $'[global] \n\
index-url = https://mirrors.aliyun.com/pypi/simple/ \n\
[install] \n\
trusted-host=mirrors.aliyun.com' > ~/.pip/pip.conf
RUN python3 -m pip install -U ipython
