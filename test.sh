#!/bin/bash -ex

docker build -t app-test --target test .

# create file for logs
rm -fr logs
mkdir -p logs
touch logs/service.log

docker run \
    --rm \
    -it \
    -v "${PWD}/logs:/logs:rw" \
    app-test
