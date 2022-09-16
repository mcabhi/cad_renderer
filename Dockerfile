FROM python:3.9.14-alpine3.16

USER root

COPY ca-certificates.crt /tmp/ca-certificates.crt
RUN cat /tmp/ca-certificates.crt >> /etc/ssl/certs/ca-certificates.crt

RUN apk update
RUN apk add --no-cache \
# installs gcc which is required for Cairo
    build-base \
# installs Cairo stuff
    cairo-dev cairo cairo-tools

COPY ./requirements.txt /var/tmp/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /var/tmp/requirements.txt

WORKDIR /app

