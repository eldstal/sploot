#!/bin/bash

KIND=${1}
URL=${2}

function usage() {
    echo "$(basename $BASH_SOURCE) <victim|double|partial> hostname"
    exit 1
}

function keep_trying {
    URL=$1
    NORMAL_REGEX=$2
    COUNT=${3:--1}
    while [ $COUNT -ne 0 ]; do
        curl --silent "${URL}" | grep -v -E "${NORMAL_REGEX}"

        let COUNT=${COUNT}-1
    done
}


[ -z "$HOST" ] && usage
[ -z "$KIND" ] && usage


if [ "$KIND" == "double" ]; then
    keep_trying "${HOST}/double" "triggered a double-response attack" -1

elif [ "$KIND" == "partial" ]; then
    keep_trying "${HOST}/partial" "triggered a partial response" -1

else
    keep_trying "${HOST}/" "here's your content"
fi
