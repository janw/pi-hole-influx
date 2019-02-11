FROM python:3.6-alpine

LABEL maintainer="mail@janwillhaus.de"

WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY piholeinflux.py config.ini.example ./

CMD [ "python", "./piholeinflux.py" ]