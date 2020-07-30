#!/usr/bin/env bash

set -euo pipefail

function build() {
  docker build $1 -t retenet/$1 --no-cache
}

if [ "${1-}" = "build" ]; then
  BROWSER="$2"

  if test -d $BROWSER; then
    build $BROWSER
    exit 0
  elif [ "$BROWSER" == "all" ]; then
    for d in *
    do
        if test -d $d; then
            build "$d"
        fi
    done
    exit 0
  else
    echo "Invalid Image Name"
    exit 1
  fi
fi

if [ "${1-}" = "release" ]; then
  if [ "$#" -eq 1 ]; then
    for d in *
    do
        if test -d $d; then
            IMAGE="netvisor/$d"
            docker push "$IMAGE"
        fi
    done
    exit 0
  fi

  BROWSER="$2"
  if test -d $BROWSER; then
    build $BROWSER
    docker push "netvisor/$BROWSER"
    exit 0
  else
    echo "Invalid Image Name"
    exit 1
  fi

  exit 0
fi
