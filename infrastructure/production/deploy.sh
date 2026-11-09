#!/bin/sh
docker context use lgweb
docker compose \
    --env-file ./infrastructure/production/.env \
    --env-file ./infrastructure/production/.env.server \
    -p lgweb \
    -f ./infrastructure/production/docker-compose.yml \
    pull
docker compose \
    --env-file ./infrastructure/production/.env \
    --env-file ./infrastructure/production/.env.server \
    -p lgweb \
    -f ./infrastructure/production/docker-compose.yml \
    run --rm --no-deps cron ./server/migrations
docker compose \
    --env-file ./infrastructure/production/.env \
    --env-file ./infrastructure/production/.env.server \
    -p lgweb \
    -f ./infrastructure/production/docker-compose.yml \
    up -d
