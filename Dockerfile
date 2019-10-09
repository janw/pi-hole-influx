ARG BUILD_FROM=python:3.6-alpine
FROM $BUILD_FROM
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN apk add --no-cache tini && \
    pip install --no-cache-dir -r requirements.txt

COPY user.toml.example ./user.toml
COPY default.toml ./
COPY piholeinflux ./piholeinflux

ENTRYPOINT [ "tini", "--" ]
CMD [ "python", "-m", "piholeinflux" ]
