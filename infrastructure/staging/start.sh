#!/bin/sh
docker compose \
    -p lgweb-staging \
    -f ./infrastructure/staging/docker-compose.yml \
    build
docker compose \
    -p lgweb-staging \
    -f ./infrastructure/staging/docker-compose.yml \
    run --rm --no-deps cron ./server/migrations
docker compose \
    -p lgweb-staging \
    -f ./infrastructure/staging/docker-compose.yml \
    up
