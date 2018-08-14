FROM ubuntu:16.04 as builder

# add docker user
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo \
 && useradd -ms /bin/bash docker \
 && echo 'docker ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && usermod -aG sudo docker \
 && chown -R docker /usr/local/bin \
 && sudo apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
USER docker

RUN sudo apt-get update \
 && sudo apt-get install -y --no-install-recommends \
      python \
      python-pip \
      python-dev \
      git \
      gcc \
      g++ \
      build-essential \
      libxml2-dev \
      libxslt-dev \
      libexpat1-dev \
      make \
      cmake \
      libtool \
      automake \
      autoconf \
      libfreetype6-dev \
      libpng-dev \
      liblapack-dev \
      gfortran \
      ca-certificates \
      openssl \
 && sudo apt-get clean \
 && sudo rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install packages
# FIXME this is a build-time dependency
RUN sudo pip install --no-cache-dir setuptools \
 && sudo pip install --no-cache-dir \
      matplotlib \
      pyserial \
      scipy \
      pexpect \
      future \
      mavproxy \
      pymavlink==2.2.10

RUN sudo mkdir -p /opt \
 && sudo chown -R docker /opt \
 && cd /opt \
 && git clone git://github.com/ArduPilot/ArduPilot ardupilot \
 && cd ardupilot \
 && git checkout Rover-3.4.0 \
 && git submodule update --init --recursive \
 && git config --global user.name start \
 && git config --global user.email start \
 && rm -rf .git \
 && find . -name .git -exec rm -rf {} \+ \
 && git init \
 && git add --all . \
 && git commit -m "borked" \
 && sudo chown -R docker /opt
WORKDIR /opt/ardupilot

# NOTE -mno-push-args is required by zipr
RUN ./waf configure \
        --no-submodule-update \
        CXXFLAGS="-mno-push-args" \
 && ./waf rover -j8

ENV PATH "${PATH}:/opt/ardupilot/Tools/autotest"

# install dronekit and gcovr
RUN sudo pip install --no-cache-dir \
      dronekit \
      dronekit-sitl \
      gcovr

# remove unnecessary dependencies
RUN sudo apt-get remove -y \
      libfreetype6-dev \
      libpng-dev \
      liblapack-dev \
      gfortran \
      ca-certificates \
      openssl \
      libtool \
      automake \
      autoconf

# install test harness
COPY --from=start-th /opt/start-th /tmp/start-th
RUN cd /tmp/start-th \
 && sudo pip install . \
 && sudo rm -rf /tmp/*
