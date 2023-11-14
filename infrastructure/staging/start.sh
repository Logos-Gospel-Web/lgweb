#!/bin/sh
docker compose \
    -p lgweb-staging \
    -f ./infrastructure/staging/docker-compose.yml \
    up
