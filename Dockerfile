FROM python:3.6-alpine

LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY user.toml.example ./user.toml
COPY default.toml ./
COPY piholeinflux.py ./

CMD [ "python", "./piholeinflux.py" ]
