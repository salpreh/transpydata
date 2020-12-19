FROM python:3.8-alpine

RUN mkdir /code
WORKDIR /code

COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock ./Pipfile.lock

RUN pip install pipenv
RUN pipenv install
