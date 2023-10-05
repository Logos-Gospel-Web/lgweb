FROM alpine:3.18

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'nginx' 'supervisor=~4' 'gettext' 'nodejs=~18' 'npm=~9' 'python3=~3.11' 'py3-pip=~23' &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    ln -sf /usr/bin/pip3 /usr/bin/pip &&\
    pip install wheel gunicorn

ADD package.json /lgweb/
ADD package-lock.json /lgweb/

RUN npm ci --omit=dev

ADD requirements.txt /lgweb/

RUN pip install -r requirements.txt

RUN pip uninstall -y wheel &&\
    apk del 'build-base' 'py3-pip'

ADD . /lgweb/

RUN mv infrastructure/production/nginx.conf /etc/nginx/http.d/default.conf &&\
    mv infrastructure/production/supervisor.conf / &&\
    rm -r infrastructure

ENV MODE production
ENV STATIC_ROOT /static
ENV MEDIA_ROOT /uploads
ENV DB_ROOT /db/db.sqlite3
ENV CONTACT_DB_ROOT /db/contact.sqlite3
ENV ANALYTICS_DB_ROOT /db/analytics.sqlite3

RUN python manage.py compilemessages &&\
    python manage.py collectstatic --no-input &&\
    rm -rf node_modules &&\
    apk del 'nodejs' 'npm'

ENV ERROR_LOG_FILE /reports/error.log

EXPOSE 80

CMD [ "supervisord", "-c", "/supervisor.conf" ]
