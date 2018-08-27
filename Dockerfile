FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install uuid-dev

ARG ENV=develop

RUN mkdir -p /webapp
COPY ./requirements /webapp/requirements
WORKDIR /webapp

RUN pip install --upgrade pip && \
    pip install -r requirements/${ENV}.txt && \
    pip install ipdb
