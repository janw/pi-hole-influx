ARG BUILD_FROM=python:3.6-alpine
FROM registry.gitlab.com/janw/python-poetry:3.6-alpine as reqexport

WORKDIR /src
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt -o requirements.txt

ARG BUILD_FROM=python:3.6-alpine
FROM $BUILD_FROM
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=reqexport /src/requirements.txt ./
RUN apk add --no-cache tini && \
    pip install --no-cache-dir -r requirements.txt

COPY user.toml.example ./user.toml
COPY default.toml ./
COPY pi_hole_influx ./pi_hole_influx

ENTRYPOINT [ "tini", "--" ]
CMD [ "python", "-m", "pi_hole_influx" ]
