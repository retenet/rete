#!/bin/bash

MORE_ARGS=""
BROWSER_PROFILE_DIR="/home/user/profile"
PROFILE_NAME=${PROFILE_NAME:-tmp}

mkdir -p $BROWSER_PROFILE_DIR

if [ ! -z "$PROXY" ]; then

    # extract the protocol
    proto="$(echo $PROXY | grep :// | sed -e's,^\(.*://\).*,\1,g')"
    # remove the protocol
    url="$(echo ${PROXY/$proto/})"
    # extract the user (if any)
    user="$(echo $url | grep @ | cut -d@ -f1)"
    # extract the host and port
    hostport="$(echo ${url/$user@/} | cut -d/ -f1)"
    # by request host without port
    host="$(echo $hostport | sed -e 's,:.*,,g')"
    # by request - try to extract the port
    port="$(echo $hostport | sed -e 's,^.*:,:,g' -e 's,.*:\([0-9]*\).*,\1,g' -e 's,[^0-9],,g')"
    # extract the path (if any)
    path="$(echo $url | grep / | cut -d/ -f2-)"

    MORE_ARGS+=" --proxy-server=${proto}${hostport} "
fi

# Setup DoH?
if [ -n "${DOH}" ]; then
    MORE_ARGS+=" --enable-features=\"dns-over-https<DoHTrial\" --force-fieldtrials=\"DoHTrial/Group1\" --force-fieldtrial-params=\"DoHTrial.Group1:server/https://${DOH}/dns-query/method/POST\" "
fi

args=("$@")
if [ ! -z "$MORE_ARGS" ]; then
    args+=("$MORE_ARGS")
fi

exec "${args[@]}"
