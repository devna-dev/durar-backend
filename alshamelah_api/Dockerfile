# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=alshamelah.settings.dev

RUN pip install --upgrade pip

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev libjpeg \
    && pip install psycopg2

RUN apk add --no-cache bash

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt

# copy project
COPY . /usr/src/app/

RUN chmod 666 /usr/src/app/media

RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh


# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
