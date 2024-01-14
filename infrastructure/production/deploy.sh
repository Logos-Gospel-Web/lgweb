#!/bin/sh
docker context use lgweb
docker compose \
    -p lgweb \
    -f ./infrastructure/production/docker-compose.yml \
    up -d --build
