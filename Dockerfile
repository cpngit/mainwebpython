FROM python:3-alpine
MAINTAINER Cassio Nunes <cassiopereira.nunes@gmail.com>

ENV INSTALL_PATH /App
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "App.app:create_app()"
