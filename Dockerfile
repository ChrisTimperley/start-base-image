FROM alpine:3.7 AS builder

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
      libxml2-dev \
      libxslt-dev \
      expat-dev \
      make \
      cmake \
      libtool \
      automake \
      autoconf \
      freetype-dev \
      libpng-dev \
      lapack-dev \
      gfortran \
      ca-certificates \
      openssl \
 && python -m ensurepip \
 && sudo rm -r /usr/lib/python*/ensurepip

# SEE: https://github.com/gmyoungblood-parc/docker-alpine-ardupilot/blob/master/Dockerfile#L81
RUN sudo ln -s /usr/include/locale.h /usr/include/xlocale.h \
 && sudo sed -i 's/, int,/, unsigned int,/' /usr/include/assert.h

# install packages
# FIXME this is a build-time dependency
RUN sudo pip install --no-cache-dir \
      matplotlib \
      pyserial \
      scipy \
      pexpect \
      future \
      mavproxy \
      pymavlink==2.2.10

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

# install test harness
COPY --from=start-th /opt/start-th /tmp/start-th
RUN cd /tmp/start-th \
 && sudo pip install . \
 && sudo rm -rf /tmp/*

COPY mission.txt /experiment/mission.txt
COPY attack.py /experiment/attack.py
COPY scenario.cfg /experiment/config/scenario.cfg
COPY default.cfg /experiment/config/default.cfg
RUN sudo chown -R docker /experiment \
 && mkdir -p /experiment/source/build/sitl/bin \
 && ln -s /opt/ardupilot/build/sitl/bin/ardurover \
      /experiment/source/build/sitl/bin/ardurover

## it appears that JSBsim isn't required to run the tests
# WORKDIR /experiment
# ENV JSBSIM_REVISION 9cc2bf1
# ENV JSBSIM_REVISION 57af0084c639d411d78f7797a98e165994de3bd4
# RUN git clone git://github.com/tridge/jsbsim /opt/jsbsim \
# && cd /opt/jsbsim \
# && git checkout "${JSBSIM_REVISION}" \
# &&  ./autogen.sh --enable-libraries \
# && make -j
# RUN cd /opt/jsbsim \
#  && sudo make install
# ENV PATH "${PATH}:/opt/jsbsim/src"
# ENV PATH "/usr/games:${PATH}"
ENV PATH "${PATH}:/opt/ardupilot/Tools/autotest"

# install dronekit
RUN sudo pip install --no-cache-dir dronekit dronekit-sitl

# remove unnecessary dependencies
RUN sudo apk del \
      freetype-dev \
      libpng-dev \
      lapack-dev \
      gfortran \
      ca-certificates \
      openssl \
      libtool \
      automake \
      autoconf

RUN sudo apk add --no-cache libc6-compat
RUN sudo chown -R docker /opt

## we need to build glibc to allow coverage information to be collected
## https://github.com/frol/docker-alpine-glibc/blob/master/Dockerfile
#ENV LANG=C.UTF-8
#USER root
#RUN ALPINE_GLIBC_BASE_URL="https://github.com/sgerrand/alpine-pkg-glibc/releases/download" \
# && ALPINE_GLIBC_PACKAGE_VERSION="2.27-r0" \
# && ALPINE_GLIBC_BASE_PACKAGE_FILENAME="glibc-$ALPINE_GLIBC_PACKAGE_VERSION.apk" \
# && ALPINE_GLIBC_BIN_PACKAGE_FILENAME="glibc-bin-$ALPINE_GLIBC_PACKAGE_VERSION.apk" \
# && ALPINE_GLIBC_I18N_PACKAGE_FILENAME="glibc-i18n-$ALPINE_GLIBC_PACKAGE_VERSION.apk" \
# && apk add --no-cache --virtual=.build-dependencies wget ca-certificates \
# && wget -nv \
#        https://raw.githubusercontent.com/sgerrand/alpine-pkg-glibc/master/sgerrand.rsa.pub \
#        -O /etc/apk/keys/sgerrand.rsa.pub \
# && wget \
#        "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
#        "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
#        "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_I18N_PACKAGE_FILENAME" \
# && apk add --no-cache \
#        "$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
#        "$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
#        "$ALPINE_GLIBC_I18N_PACKAGE_FILENAME" \
# && rm /etc/apk/keys/sgerrand.rsa.pub \
# && /usr/glibc-compat/bin/localedef --force --inputfile POSIX --charmap UTF-8 "$LANG" || true \
# && echo "export LANG=$LANG" > /etc/profile.d/locale.sh \
# && apk del glibc-i18n \
# && rm /root/.wget-hsts \
# && apk del .build-dependencies \
# && rm "$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
#       "$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
#       "$ALPINE_GLIBC_I18N_PACKAGE_FILENAME"
#USER docker

RUN sudo pip install --no-cache-dir gcovr
