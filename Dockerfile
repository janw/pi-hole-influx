FROM python:3.10-alpine
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN apk add --no-cache 'tini>=0.19' && \
    pip install --no-cache-dir -r requirements.txt

COPY user.toml.example ./user.toml
COPY default.toml ./
COPY piholeinflux.py ./

ENTRYPOINT [ "tini", "--" ]
CMD [ "python", "./piholeinflux.py" ]
