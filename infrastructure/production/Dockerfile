FROM python:3.11-alpine

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'nginx' 'supervisor=~4' 'gettext' &&\
    pip install wheel gunicorn

ADD requirements.txt /lgweb/

RUN pip install -r requirements.txt

RUN apk del 'build-base' &&\
    pip uninstall -y wheel

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
    python manage.py collectstatic --no-input

ENV ERROR_LOG_FILE /reports/error.log

CMD [ "supervisord", "-c", "/supervisor.conf" ]
