# syntax=docker/dockerfile:1.21

# ========================================

FROM alpine:3.23.3 AS compiler

WORKDIR /assets

RUN apk add --no-cache 'nodejs=~24' 'npm=~11'

COPY assets/package*.json /assets/

RUN npm ci --omit=dev

COPY ./assets /assets/

RUN npx rspack --mode=production --env output=/compiled

# ========================================

FROM alpine:3.23.3 AS base

WORKDIR /lgweb

ENV TZ=Asia/Hong_Kong

RUN apk add --no-cache 'abiword=~3' 'abiword-plugin-openxml=~3' 'build-base' 'gettext' 'python3=~3.12' 'py3-pip=~25' 'tzdata' &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    ln -sf /usr/bin/pip3 /usr/bin/pip &&\
    pip install gunicorn --break-system-packages

ADD requirements.txt /lgweb/

RUN pip install -r requirements.txt --break-system-packages &&\
    rm requirements.txt

RUN apk del 'build-base' 'py3-pip'

ENV MODE=production
ENV STATIC_ROOT=/static
ENV DB_ROOT=/db/db.sqlite3
ENV CONTACT_DB_ROOT=/db/contact.sqlite3
ENV ANALYTICS_DB_ROOT=/db/analytics.sqlite3
ENV ANALYTICS_TEMP_DB_ROOT=/db/analytics_temp.sqlite3
ENV ERROR_LOG_FILE=/reports/error.log

# ========================================

FROM base AS preprocessor

COPY --parents \
    --exclude=app/migrations/ \
    --exclude=app/management/ \
    ./manage.py ./project ./locales ./app /lgweb/

# Unset the variable to prevent logging
ENV ERROR_LOG_FILE=

RUN python manage.py collectstatic --no-input &&\
    python manage.py compilemessages &&\
    rm -rf /lgweb/app/static

# ========================================

FROM base AS main

COPY --from=preprocessor /lgweb /lgweb

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application" ]

# ========================================

FROM base AS cron

COPY --from=preprocessor /lgweb /lgweb
COPY --parents ./app/management /lgweb/
COPY --chmod=600 ./server/crontab /etc/crontabs/root
COPY --chmod=700 ./server/cron/* /cron/

CMD [ "crond", "-f", "-d", "6" ]

# ========================================

FROM base AS migrations

COPY --from=preprocessor /lgweb /lgweb
COPY --parents ./app/migrations /lgweb/
COPY --parents --chmod=700 ./server/migrations /lgweb/

CMD [ "./server/migrations" ]

# ========================================

FROM caddy:2.11-alpine AS server

ENV CACHE_CONTROL='max-age=3600'

COPY ./server/Caddyfile /etc/caddy/Caddyfile
COPY public /public
COPY --from=preprocessor /static /static
COPY --from=compiler /compiled /compiled
