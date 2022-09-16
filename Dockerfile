FROM python:3.9.14-alpine3.16



COPY ./requirements.txt /var/tmp/
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r /var/tmp/requirements.txt

WORKDIR /app

