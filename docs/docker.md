# Docker Introduction

## Installation

1. Install Docker

   run the shell scrip

```shell
   curl -sSL https://get.docker.com/ | sh
```

   or the shell provided by Alibaba Cloud

```shell
   curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/internet | sh -
```

   or the shell provided by DaoCloud

```shell
   curl -sSL https://get.daocloud.io/docker | sh
```

2. Install Nvidia Docker2

```shell
# If you have nvidia-docker 1.0 installed: we need to remove it and all existing GPU containers
ocker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker
ps -q -a -f volume={} | xargs -r docker rm -f
sudo apt-get purge -y nvidia-docker
# Add the package repositories
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add ¨C
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu16.04/amd64/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
# Install nvidia-docker2 and reload the Docker daemon configuration sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo pkill -SIGHUP dockerd
# Test nvidia-smi with the latest official CUDA image
docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi
```
