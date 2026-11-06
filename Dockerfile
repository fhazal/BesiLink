FROM python:3.13-alpine

RUN adduser -D -H -u 10000 pylink

VOLUME /pylink

COPY . /pylink-src

# Fork change: "setup.py install" is deprecated/removed in current setuptools; install with pip.
RUN cd /pylink-src && pip3 install --no-cache-dir -r requirements-docker.txt \
    && pip3 install --no-cache-dir . \
    && rm -r /pylink-src

USER pylink
WORKDIR /pylink

# Run in no-PID file mode by default
CMD ["pylink", "-n"]
