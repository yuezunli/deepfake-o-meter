# ==================================================================
# Thanks brother xwj for providing the source Dockfile
# module list
# ------------------------------------------------------------------
# python        3.7    (conda)
# pytorch       1.0.1  (pip)
# ==================================================================
FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
MAINTAINER zhangcong

RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/http:\/\/lt\./http:\/\//g' /etc/apt/sources.list && \
    apt-get -y update  && \
    apt-get -y install wget vim cmake && \
    apt-get -y install apt-file &&\
    apt-file update && \
    apt-file search libSM.so.6 &&\
    apt-get -y install libsm6 libxrender1 python-qt4 openssh-client openssh-server git &&\
    apt-get -y install libxrender1  &&\
    apt -y install python-qt4  &&\
    apt-get -y install openssh-client sudo openssh-server  &&\
    apt-get -y install git  &&\
# ==================================================================
# anaconda
# ------------------------------------------------------------------
    wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-5.3.1-Linux-x86_64.sh -O ~/anaconda3.sh && \
    /bin/bash ~/anaconda3.sh -b -p /home/anaconda3 && rm ~/anaconda3.sh

ENV PATH=/home/anaconda3/bin:$PATH \
    LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/cuda-9.0/lib64:$LD_LIBRARY_PATH
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
        moviepy==1.0.3  --ignore-installed\
        dlib==19.21.0\
        torch==1.4.0 \
        torchvision==0.5.0 \
        albumentations==0.4.5 \
        opencv_python==3.4.10.35 \
        efficientnet_pytorch==0.6.3 \
        matplotlib==3.1.0 \
        scikit-learn \
        Pillow==7.1.2 \
        matplotlib==3.1.0 \
        && \
    pip install \
        pretrainedmodels==0.7.4 \
        easydict==1.9 \
        && \
    pip uninstall numpy -y && \
    pip uninstall numpy -y && \
    pip install numpy && \
    conda clean -y --all && \
# ==================================================================
# config & cleanup
# ------------------------------------------------------------------
    ldconfig && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/*
EXPOSE 6006
