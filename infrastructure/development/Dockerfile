FROM alpine:3.23.3

WORKDIR /lgweb

RUN apk add --no-cache 'abiword=~3' 'build-base' 'gettext' 'nodejs=~24' 'npm=~11' 'python3=~3.12' 'py3-pip=~25' &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    ln -sf /usr/bin/pip3 /usr/bin/pip

ENV TZ=Asia/Hong_Kong

EXPOSE 8000
