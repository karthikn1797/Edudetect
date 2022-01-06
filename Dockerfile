FROM tiangolo/meinheld-gunicorn:python3.9
# FROM python:3.9-slim-buster
# FROM tiangolo/uwsgi-nginx-flask:python3.8
# FROM ubuntu:18.04

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN apt-get update -y && \
    apt-get install \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev \
    ffmpeg \
    libsm6 \
    libxext6 -y

# RUN apt-get install ffmpeg libsm6 libxext6 -y

RUN pip install dlib
RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]