# ==================================================================
# Thanks brother xwj for providing the source Dockfile
# module list
# ------------------------------------------------------------------
# python        2.7    (conda)
# pytorch       1.0.1  (pip)
# ==================================================================
FROM nvidia/cuda:8.0-cudnn6-runtime-ubuntu16.04
MAINTAINER zhangcong

RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN sed -i 's/http:\/\/lt\./http:\/\//g' /etc/apt/sources.list

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get -y update && \
    apt-get -y install wget vim cmake bzip2&& \
    apt-get -y install apt-file && \
    apt-file update && \
    apt-file search libSM.so.6 &&\
    apt-get -y install libsm6 libxrender1 python-qt4 openssh-client openssh-server git &&\
    apt-get -y install libxrender1  &&\
    apt -y install python-qt4  &&\
    apt-get -y install openssh-client sudo openssh-server  &&\
    apt-get -y install git
# ==================================================================
# anaconda
# ------------------------------------------------------------------
RUN wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda2-5.0.0-Linux-x86_64.sh -O ~/anaconda.sh
RUN /bin/bash ~/anaconda.sh -b -p /home/anaconda
RUN rm ~/anaconda.sh

ENV PATH=/home/anaconda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/cuda-8.0/lib64:$LD_LIBRARY_PATH
# ==================================================================
# conda source and pip source
# ------------------------------------------------------------------
RUN conda config --set show_channel_urls yes && \
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ && \
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ && \
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/ && \
    mkdir /home/.pip && \
    echo "[global]" > /home/.pip/pip.conf && \
    sed -i -e "\$atrusted-host=mirrors.aliyun.com" /home/.pip/pip.conf && \
    sed -i -e "\$aindex-url=http://mirrors.aliyun.com/pypi/simple/" /home/.pip/pip.conf && \
    pip install --upgrade pip && \
    pip install \
        tensorflow-gpu==1.3.0 \
        easydict==1.7 \
        opencv-python==3.4.5.20 \
        moviepy==1.0.3 \
        && \
    conda clean -y --all && \
    conda install -c menpo dlib && \
    conda install -c conda-forge matplotlib && \
# ==================================================================
# config & cleanup
# ------------------------------------------------------------------
    ldconfig && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/*
EXPOSE 6006
