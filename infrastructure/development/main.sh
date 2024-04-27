#!/bin/sh
docker compose \
    -p lgweb-dev \
    -f ./infrastructure/development/docker-compose.yml \
    up
