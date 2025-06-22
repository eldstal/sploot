#!/bin/bash

KIND=${1}
HOST=${2}

function usage() {
    echo "$(basename $BASH_SOURCE) <victim|double|partial> hostname"
    exit 1
}

function keep_trying {
    URL=$1
    NORMAL_REGEX=$2
    while true; do
        curl --silent "${URL}" | grep -v -E "${NORMAL_REGEX}"
    done
}


[ -z "$HOST" ] && usage
[ -z "$KIND" ] && usage


if [ "$KIND" == "double" ]; then
    keep_trying "http://${HOST}/double" "triggered a double-response attack"

elif [ "$KIND" == "partial" ]; then
    keep_trying "http://${HOST}/partial" "triggered a partial response"

else
    keep_trying "http://${HOST}/" "here's your content"
fi
