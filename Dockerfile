FROM python:3.9.14-alpine3.16



COPY ./requirements.txt /var/tmp/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /var/tmp/requirements.txt

WORKDIR /app

