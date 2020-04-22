FROM jupyter/scipy-notebook:cf6258237ff9

RUN apt-get update && \
    apt-get install git python3-pip python3-venv -y &&\
    pip3 install poetry &&\
    mkdir -p /sandbox/code/github/js-next
RUN git clone https://github.com/js-next/js-ng.git /sandbox/code/github/js-next/js-ng
WORKDIR /sandbox/code/github/js-next/js-ng
RUN poetry update && poetry install

