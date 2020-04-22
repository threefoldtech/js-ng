FROM threefoldtech/js-ng
# install the notebook package
RUN apt-get install python3-pip && \
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
RUN chown -R ${NB_UID} /sandbox
RUN git clone https://github.com/js-next/js-ng/tree/development_binder /sandbox/code/github/js-next/js-ng2
RUN ln -s /sandbox/code/github/js-next/js-ng2 ${HOME}/js-ng
USER ${USER}

ENTRYPOINT []
