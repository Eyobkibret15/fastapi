#!/bin/bash -ex

docker volume create fast-library-db || true

docker build -t app --target app .

docker run --rm -it -p 8000:8000 -v fast-library-db:/app/db app