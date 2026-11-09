FROM alpine:3.24.4

WORKDIR /lgweb

RUN apk add --no-cache 'abiword' 'abiword-plugin-openxml' 'build-base' 'gettext' 'nodejs' 'npm' 'python3' 'py3-pip' 'cairo' &&\
    ln -sf /usr/bin/python3 /usr/bin/python &&\
    ln -sf /usr/bin/pip3 /usr/bin/pip

ENV TZ=Asia/Hong_Kong

EXPOSE 8000
