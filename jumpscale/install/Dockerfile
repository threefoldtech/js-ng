FROM threefoldtech/phusion:19.10
RUN apt-get update && \
    apt-get install git python3-pip python3-venv -y &&\
    pip3 install poetry &&\
    mkdir -p /sandbox/code/github/js-next
RUN git clone https://github.com/js-next/js-ng.git /sandbox/code/github/js-next/js-ng
WORKDIR /sandbox/code/github/js-next/js-ng
RUN poetry config virtualenvs.create false \
    && poetry install
ENTRYPOINT ["/sbin/my_init"]