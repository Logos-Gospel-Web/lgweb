docker compose `
    -p lgweb-dev `
    -f .\infrastructure\development\docker-compose.yml `
    run --rm --service-ports lgweb-dev
