#!/bin/bash

KIND=${1}
URL=${2}

function usage() {
    echo "$(basename $BASH_SOURCE) <victim|double|partial> http://host"
    exit 1
}

function keep_trying {
    URL=$1
    PREFIX_REGEX=$2
    COUNT=${3:--1}
    while [ $COUNT -ne 0 ]; do
        sleep 0.1
        local PARAM=$RANDOM
        #curl --http1.1 --silent "${URL}" "${URL}" "${URL}" | grep -v -E "${NORMAL_REGEX}"
        curl --http1.1 --silent "${URL}?${PARAM}" | grep -v -E "${NORMAL_REGEX}=${PARAM}"

        let COUNT=${COUNT}-1
    done
}


[ -z "$URL" ] && usage
[ -z "$KIND" ] && usage


if [ "$KIND" == "double" ]; then
    keep_trying "${URL}/double" "First" -1

elif [ "$KIND" == "partial" ]; then
    keep_trying "${URL}/partial" "First" -1

else
    keep_trying "${URL}/" "Normal"
fi
