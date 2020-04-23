FROM threefoldtech/js-ng
# install the notebook package
# RUN apt-get install python3-pip python3-venv -y &&\
#     pip3 install poetry &&\
RUN pip3 install --no-cache notebook

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
# Cloning from the right branch 
# RUN git clone --branch development_binder https://github.com/js-next/js-ng  /sandbox/code/github/js-next/js-ng2
WORKDIR /sandbox/code/github/js-next/js-ng
RUN git checkout development_binder
# link the cloned path to ${HOME}/js-ng as it is the default path for binder to start
RUN ln -s /sandbox/code/github/js-next/js-ng ${HOME}/js-ng
# Change user to the one given by binder
USER ${USER}

WORKDIR ${HOME}/js-ng

# USER root
# RUN poetry config virtualenvs.create false \
#     && poetry install --no-interaction --no-ansi

# Creating /.config file which will be used in runtime
RUN mkdir -p ${HOME}/.config/jumpscale
RUN chown -R ${NB_UID} ${HOME}/.config/jumpscale

ENTRYPOINT []
