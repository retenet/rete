FROM ubuntu:bionic
LABEL maintainer="Craig West <dev@exploit.design"

ENV DEBIAN_FRONTEND=noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Softwarez
RUN apt-get update && \
 apt-get -y upgrade -y && \
 apt-get -y dist-upgrade && \
 apt-get install -y \
   browser-plugin-freshplayer-pepperflash \
   firefox \
   fonts-noto \
   fonts-noto-cjk \
   fonts-noto-color-emoji \
   libnss3-tools \
   libpango1.0-0 \
   locales \
   pepperflashplugin-nonfree \
   pulseaudio \
   --no-install-recommends && \
 rm -fr /var/lib/apt/lists/*

# Locale
# Create User
RUN locale-gen en_US.UTF-8 && \
 echo 'LANG=en_US.UTF-8' > /etc/locale.conf && \
 useradd -m -G audio,video -s /bin/bash user

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


COPY ./entrypoint.sh /
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

COPY ./extensions /usr/lib/firefox-addons/extensions

USER user
WORKDIR /home/user

ENV LC_ALL=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV TZ=UTC

CMD ["firefox", "--no-remote", "--profile", "/home/user/profile"]
