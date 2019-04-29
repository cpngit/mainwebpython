FROM python:3-alpine
MAINTAINER Cassio Nunes <cassiopereira.nunes@gmail.com>

RUN apk update && apk add build-base postgresql-dev

ENV INSTALL_PATH /App
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .

CMD gunicorn -c "python:config.gunicorn" "App.app:create_app()"
