FROM alpine:3.7

# add docker user
RUN apk add --no-cache bash sudo shadow \
 && adduser -D -h /home/docker -s /bin/bash docker \
 && echo 'docker ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && groupadd sudo \
 && usermod -aG sudo docker \
 && chown -R docker /usr/local/bin
USER docker

RUN sudo apk add --no-cache \
      python \
      py-pip \
      python-dev \
      git \
      gcc \
      g++ \
      linux-headers \
      musl-dev \
      libxml2-dev \
      libxslt-dev \
 && python -m ensurepip \
 && sudo rm -r /usr/lib/python*/ensurepip

# SEE: https://github.com/gmyoungblood-parc/docker-alpine-ardupilot/blob/master/Dockerfile#L81
RUN sudo ln -s /usr/include/locale.h /usr/include/xlocale.h \
 && sudo sed -i 's/, int,/, unsigned int,/' /usr/include/assert.h

# install packages
# FIXME this is a build-time dependency
RUN pip install --user --no-cache-dir \
      statistics \
      future \
      pexpect \
      geopy \
      dronekit \
      dronekit-sitl

RUN sudo mkdir /opt \
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
 && git commit -m "borked"
WORKDIR /opt/ardupilot

# alpine uses musl instead of glibc
# SEE: https://github.com/gmyoungblood-parc/docker-alpine-ardupilot/blob/master/Dockerfile#L81
RUN sed -i 's/feenableexcept(exceptions);/\/\/feenableexcept(exceptions);/' libraries/AP_HAL_SITL/Scheduler.cpp \
 && sed -i 's/int old = fedisableexcept(FE_OVERFLOW);/int old = 1;/' libraries/AP_Math/matrix_alg.cpp \
 && sed -i 's/if (old >= 0 && feenableexcept(old) < 0)/if (0)/' libraries/AP_Math/matrix_alg.cpp \
 && sed -i "s/#include <sys\/types.h>/#include <sys\/types.h>\n\n#define TCGETS2 _IOR('T', 0x2A, struct termios2)\n#define TCSETS2 _IOW('T', 0x2B, struct termios2)/" libraries/AP_HAL_SITL/UART_utils.cpp

# NOTE -mno-push-args is required by zipr
RUN ./waf configure \
        --no-submodule-update \
        CXXFLAGS="-mno-push-args" \
 && ./waf rover -j8

# create a wheel ;-)


# install from wheel in a separate stage
