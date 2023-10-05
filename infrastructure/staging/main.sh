#!/bin/sh
docker compose \
    -p lgweb-staging \
    -f ./infrastructure/staging/docker-compose.yml \
    run --rm --service-ports lgweb-staging
