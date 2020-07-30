FROM ubuntu:latest
LABEL maintainer="Craig West <dev@exploit.design"

ENV DEV_KEY=0xEF6E286DDA85EA2A4BA7DE684E2C6E8793298290

ENV DEBIAN_FRONTEND=noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Softwarez
RUN build_deps=' ca-certificates curl gnupg xz-utils ' && \
 apt-get update && \
 apt-get -y upgrade -y && \
 apt-get -y dist-upgrade && \
 apt-get install -y \
   firefox \
   libexif-dev \
   libgl1-mesa-dri \
   libgl1-mesa-glx \
   libpulse0 \
   libasound2 \
   libasound2-plugins \
   locales \
   pulseaudio \
   $build_deps \
   --no-install-recommends && \
 rm -fr /var/lib/apt/lists/* && \
 export BUILD_VERSION="$(curl -sSL https://www.torproject.org/download/ | grep 'torbrowser' | awk -F'/' '{ print $4 }' | head -1 | tr -d '\n')" && \
 curl -sSLO https://www.torproject.org/dist/torbrowser/${BUILD_VERSION}/tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz && \
 curl -sSLO https://www.torproject.org/dist/torbrowser/${BUILD_VERSION}/tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz.asc && \
 curl -s https://openpgpkey.torproject.org/.well-known/openpgpkey/torproject.org/hu/kounek7zrdx745qydx6p59t9mqjpuhdf | gpg --import - && \
 gpg --output ./tor.keyring --export ${DEV_KEY} && \
 gpgv --keyring ./tor.keyring tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz.asc tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz && \
 tar xf tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz && \
 rm tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz && \
 rm tor-browser-linux64-${BUILD_VERSION}_en-US.tar.xz.asc && \
 rm tor.keyring && \
 apt-get purge -y --auto-remove $build_deps

# Locale
# Create User
RUN locale-gen en_US.UTF-8 && \
 echo 'LANG=en_US.UTF-8' > /etc/locale.conf && \
 useradd -m -s /bin/bash user && \
 mv tor-browser_en-US /home/user/ && \
 chown -R user:user /home/user/tor-browser_en-US

# Harden my Shiz
RUN \
 rm -fr /var/spool/cron && \
 rm -fr /etc/crontabs && \
 rm -fr /etc/periodic && \
 rm -fr /etc/init.d && \
 rm -fr /lib/rc && \
 rm -fr /etc/conf.d && \
 rm -fr /etc/inittab && \
 rm -fr /etc/runlevels && \
 rm -fr /etc/rc.conf && \
 rm -fr /etc/sysctl* && \
 rm -fr /etc/modprobe.d && \
 rm -fr /etc/modules && \
 rm -fr /etc/mdev.conf && \
 rm -fr /etc/acpi && \
 rm -fr /root && \
 rm -f /etc/fstab && \
 sed -i -r '/^(user|root|nobody)/!d' /etc/group && \
 sed -i -r '/^(user|root|nobody)/!d' /etc/passwd && \
 sed -i -r '/^user:/! s#^(.*):[^:]*$#\1:/sbin/nologin#' /etc/passwd && \
 find /bin /etc /lib /sbin /usr -xdev -type f -regex '.*-$' -exec rm -f {} + && \
 find /bin /etc /lib /sbin /usr -xdev -type f -a -perm -4000 -delete && \
 find /bin /etc /lib /sbin /usr -xdev \( \
  -name hexdump -o \
  -name chgrp -o \
  -name chmod -o \
  -name chown -o \
  -name ln -o \
  -name od -o \
  -name strings -o \
  -name su \
  \) -exec rm -rf {} + && \
 find /bin /etc /lib /sbin /usr -xdev -type l -exec test ! -e {} \; -delete

USER user
WORKDIR /home/user

ENV LC_ALL=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

CMD ["./tor-browser_en-US/Browser/start-tor-browser"]
