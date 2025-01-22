FROM alpine:3.19.1 as base

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'nginx' 'supervisor=~4' 'gettext' 'python3=~3.11' 'py3-pip=~23' 'tzdata' &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    ln -sf /usr/bin/pip3 /usr/bin/pip &&\
    pip install gunicorn --break-system-packages

ENV TZ=Asia/Hong_Kong

ADD requirements.txt /lgweb/

RUN pip install -r requirements.txt --break-system-packages

RUN apk del 'build-base' 'py3-pip'

ENV MODE production
ENV STATIC_ROOT /static
ENV COMPILED_ROOT /compiled
ENV DB_ROOT /db/db.sqlite3
ENV CONTACT_DB_ROOT /db/contact.sqlite3
ENV ANALYTICS_DB_ROOT /db/analytics.sqlite3

FROM base as builder

RUN apk add --no-cache 'nodejs=~20' 'npm=~10'

COPY package.json /lgweb/
COPY package-lock.json /lgweb/

RUN npm ci --omit=dev

COPY . /lgweb/

CMD [ "./infrastructure/production/build" ]

FROM base as main

COPY . /lgweb/

RUN python manage.py compilemessages

ENV ERROR_LOG_FILE /reports/error.log

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application" ]

FROM caddy:2.7-alpine as server

ENV CACHE_CONTROL 'max-age=3600'

COPY ./configs/Caddyfile /etc/caddy/Caddyfile
COPY public /public

FROM main as cron

RUN apk add --no-cache 'nodejs=~20' 'npm=~10'

RUN cd lib/isbot && npm ci --omit=dev

RUN cp ./infrastructure/production/crontab /etc/crontabs/root &&\
    chmod 600 /etc/crontabs/root &&\
    chmod 700 ./infrastructure/production/cron/*

CMD [ "crond", "-f", "-d", "6" ]
