FROM alpine:3.19.1

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'gettext' 'nodejs=~20' 'npm=~10' 'python3=~3.11' &&\
    ln -sf /usr/bin/python3 /usr/bin/python

ENV TZ=Asia/Hong_Kong

EXPOSE 8000
