FROM python:3.11.5-slim-bullseye
RUN apt update && apt -y upgrade
WORKDIR /usr/src/app
ENV PYTHONPATH="/usr/src/app:$PYTHONPATH"
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./ ./