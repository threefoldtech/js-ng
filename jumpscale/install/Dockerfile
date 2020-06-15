FROM threefoldtech/phusion:19.10
RUN apt-get update && apt-get install git python3-pip python3-venv redis-server tmux nginx -y
RUN pip3 install poetry
RUN mkdir -p /sandbox/code/github/js-next
RUN git clone https://github.com/js-next/js-sdk.git /sandbox/code/github/js-next/js-sdk -b development
WORKDIR /sandbox/code/github/js-next/js-sdk
RUN poetry config virtualenvs.create false && poetry install
ENTRYPOINT ["/sbin/my_init"]
