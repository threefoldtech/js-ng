FROM threefoldtech/js-ng
# install the notebook package
RUN apt-get install python3-pip python3-venv -y &&\
    pip3 install poetry &&\
    pip3 install --no-cache notebook

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

WORKDIR ${HOME}

RUN chown -R ${NB_USER} /sandbox

RUN git clone --branch development_binder https://github.com/js-next/js-ng  /sandbox/code/github/js-next/js-ng2
RUN ln -s /sandbox/code/github/js-next/js-ng2 ${HOME}/js-ng

RUN chown -R ${NB_USER} /sandbox/code/github/js-next/js-ng2

RUN chown -R ${NB_USER} ${HOME}/js-ng
USER ${USER}

WORKDIR ${HOME}/js-ng
# RUN poetry update && poetry install
# RUN poetry shell 
# RUN jsng
RUN poetry config virtualenvs.create false \
    && poetry install $(test "production" == production && echo "--no-dev") --no-interaction --no-ansi
ENTRYPOINT []
