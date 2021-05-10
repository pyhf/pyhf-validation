FROM pyhf/pyhf-validation-root-base:root6.22.02-python3.8 as base

FROM base as builder
COPY . /code
RUN cd /code && \
    apt-get -qq -y update && \
    apt-get -qq -y install \
      git && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt-get/lists/* && \
    python -m pip install --upgrade --no-cache-dir pip setuptools wheel && \
    python -m pip install --no-cache-dir . && \
    python -m pip list

FROM base
COPY --from=builder /usr/local /usr/local
ENTRYPOINT ["/usr/local/bin/pyhf-validation"]
