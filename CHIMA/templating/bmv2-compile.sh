#!/usr/bin/env bash

set -e

PROGRAM=$1
OUT_DIR=$2
OUT_NAME=$3
OTHER_FLAGS=$4

SRC_DIR="$( cd "$( dirname "${PROGRAM}" )" >/dev/null 2>&1 && pwd )"
OUT_DIR=${OUT_DIR}

mkdir -p ${OUT_DIR}

echo
echo "## Compiling ${OUT_NAME} in ${OUT_DIR}..."

dockerImage=opennetworking/p4c
dockerRun="docker run --rm -w ${SRC_DIR} -v ${SRC_DIR}:${SRC_DIR} -v ${OUT_DIR}:${OUT_DIR} ${dockerImage}"

# Generate BMv2 JSON and P4Info.
(set -x; ${dockerRun} p4c-bm2-ss --arch v1model -o ${OUT_DIR}/${OUT_NAME}.json \
        -DTARGET_BMV2 ${OTHER_FLAGS} \
        --p4runtime-files ${OUT_DIR}/${OUT_NAME}_p4info.txt ${PROGRAM})
