# syntax=docker/dockerfile:1.21
FROM alpine:3.23.3 AS base

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'gettext' 'python3=~3.12' 'py3-pip=~25' 'tzdata' &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    ln -sf /usr/bin/pip3 /usr/bin/pip &&\
    pip install gunicorn --break-system-packages

ENV TZ=Asia/Hong_Kong

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

# ========================================

FROM base AS node

RUN apk add --no-cache 'nodejs=~24' 'npm=~11'

# ========================================

FROM base AS migrations

COPY . /lgweb/

RUN chmod +x ./infrastructure/production/migrations

CMD [ "./infrastructure/production/migrations" ]

# ========================================

FROM node AS compiler

COPY package.json /lgweb/
COPY package-lock.json /lgweb/

RUN npm ci --omit=dev

COPY . /lgweb/

RUN python manage.py collectstatic --no-input &&\
    npx rspack --mode=production --env output=/compiled

# ========================================

FROM base AS main

COPY ./manage.py /lgweb/manage.py
COPY ./project /lgweb/project
COPY ./locales /lgweb/locales
COPY --exclude=static/ \
    --exclude=scripts/ \
    --exclude=styles/ \
    --exclude=migrations/ \
    --exclude=management/ \
    ./app /lgweb/app

RUN python manage.py compilemessages

ENV ERROR_LOG_FILE=/reports/error.log

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application" ]

# ========================================

FROM node AS cron

COPY lib/isbot/package.json /lgweb/lib/isbot/
COPY lib/isbot/package-lock.json /lgweb/lib/isbot/

RUN cd lib/isbot && npm ci --omit=dev

COPY --exclude=app/static/ \
    --exclude=app/scripts/ \
    --exclude=app/styles/ \
    --exclude=app/migrations/ \
    --exclude=configs/ \
    --exclude=public/ \
    --exclude=.browserslistrc \
    --exclude=package*.json \
    --exclude=requirements.txt \
    --exclude=rspack.config.mjs \
    . /lgweb/

RUN python manage.py compilemessages &&\
    cp ./infrastructure/production/crontab /etc/crontabs/root &&\
    chmod 600 /etc/crontabs/root &&\
    chmod 700 ./infrastructure/production/cron/*

ENV ERROR_LOG_FILE=/reports/error.log

CMD [ "crond", "-f", "-d", "6" ]

# ========================================

FROM caddy:2.11-alpine AS server

ENV CACHE_CONTROL='max-age=3600'

COPY ./configs/Caddyfile /etc/caddy/Caddyfile
COPY public /public
COPY --from=compiler /static /static
COPY --from=compiler /compiled /compiled
