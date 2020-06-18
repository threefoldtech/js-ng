FROM threefoldtech/js-ng

RUN pip3 install --no-cache notebook

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

# Create User to be used by binder
RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

WORKDIR ${HOME}

RUN chown -R ${NB_USER} /sandbox
# Changing working direcotry to our code
WORKDIR /sandbox/code/github/threefoldtech/js-ng
# Checkout the branch which contain our data
#RUN git fetch --all
#RUN git checkout development_binder_examples
#RUN git pull
# link the cloned path to ${HOME}/js-ng as it is the default path for binder to start
RUN ln -s /sandbox/code/github/threefoldtech/js-ng ${HOME}/js-ng
# Change user to the one given by binder
USER ${USER}

WORKDIR ${HOME}/js-ng

USER root

# Creating /.config file which will be used in runtime
RUN mkdir -p ${HOME}/.config/jumpscale
RUN chown -R ${NB_UID} ${HOME}/.config/jumpscale

ENTRYPOINT []
