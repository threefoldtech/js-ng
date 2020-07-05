FROM threefoldtech/phusion:19.10
RUN apt-get update && apt-get install git python3-pip python3-venv redis-server tmux nginx -y
RUN pip3 install poetry
RUN mkdir -p /sandbox/code/github/threefoldtech
RUN git clone https://github.com/threefoldtech/js-ng.git /sandbox/code/github/threefoldtech/js-ng -b development
WORKDIR /sandbox/code/github/threefoldtech/js-ng
RUN poetry config virtualenvs.create false && poetry install
RUN poetry shell
RUN /etc/init.d/redis-server start
ENTRYPOINT ["/sbin/my_init"]
