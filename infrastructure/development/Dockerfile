FROM alpine:3.18

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'gettext' 'sassc' 'nodejs=~18' 'npm=~9' 'python3=~3.11' &&\
    ln -sf /usr/bin/python3 /usr/bin/python

EXPOSE 8000
