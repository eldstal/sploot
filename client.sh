#!/bin/bash

KIND=${1}
URL=${2}

function usage() {
    echo "$(basename $BASH_SOURCE) <victim|double|partial> http://host"
    exit 1
}

function keep_trying {
    URL=$1
    NORMAL_REGEX=$2
    COUNT=${3:--1}
    while [ $COUNT -ne 0 ]; do
        sleep 0.5
        curl --http1.1 --silent "${URL}" "${URL}" "${URL}" | grep -v -E "${NORMAL_REGEX}"

        let COUNT=${COUNT}-1
    done
}


[ -z "$URL" ] && usage
[ -z "$KIND" ] && usage


if [ "$KIND" == "double" ]; then
    keep_trying "${URL}/double" "triggered a double-response attack" 1

elif [ "$KIND" == "partial" ]; then
    keep_trying "${URL}/partial" "triggered a partial response" -1

else
    keep_trying "${URL}/" "here's your content"
fi
