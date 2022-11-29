FROM python:3.9-slim

WORKDIR /var/www/app

COPY requirements/ /var/www/app/requirements/

RUN pip install -r requirements/local.txt

COPY . .
