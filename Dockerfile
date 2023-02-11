FROM python:3.10-alpine
LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN apk add --no-cache 'tini>=0.19' && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /config && \
    touch /config/user.toml

COPY user.toml.example piholeinflux.py ./

ENV PIHOLE_CONFIG_FILE=/config/user.toml

ENTRYPOINT [ "tini", "--" ]
CMD [ "python", "./piholeinflux.py" ]
