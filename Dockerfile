FROM jupyter/scipy-notebook:cf6258237ff9

ARG NB_USER=test
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

USER root

# RUN adduser --disabled-password \
#     --gecos "Default user" \
#     --uid ${NB_UID} \
#     ${NB_USER}

# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

RUN apt-get update && \
    apt-get install git python3-pip python3-venv -y &&\
    pip3 install poetry &&\
    mkdir -p /sandbox/code/github/js-next
RUN git clone https://github.com/js-next/js-ng.git /sandbox/code/github/js-next/js-ng
WORKDIR /sandbox/code/github/js-next/js-ng
RUN poetry update && poetry install

