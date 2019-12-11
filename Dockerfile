FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /current
WORKDIR /current

RUN pip install pip -U

COPY . /current

RUN pip install -r requirements.txt
