FROM atlasamglab/stats-base:root6.24.02 as base

FROM base as builder
COPY . /code
RUN cd /code && \
    python -m pip install --upgrade --no-cache-dir pip setuptools wheel && \
    python -m pip install --no-cache-dir . && \
    python -m pip list

FROM base
COPY --from=builder /usr/local/venv /usr/local/venv
RUN apt-get -qq -y update && \
    apt-get -qq -y install \
      curl && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/local/venv/bin/pyhf-validation"]
