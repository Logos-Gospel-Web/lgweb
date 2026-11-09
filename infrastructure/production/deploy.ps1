docker context use lgweb
docker compose `
    -p lgweb `
    -f .\infrastructure\production\docker-compose.yml `
    build
docker compose `
    -p lgweb `
    -f .\infrastructure\production\docker-compose.yml `
    run --rm --no-deps cron ./server/migrations
docker compose `
    -p lgweb `
    -f .\infrastructure\production\docker-compose.yml `
    up -d