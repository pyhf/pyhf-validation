FROM pyhf/pyhf-validation-root-base:root6.20.00-python3.7 as base

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
COPY --from=builder /opt/condaenv /opt/condaenv
ENTRYPOINT ["/opt/condaenv/bin/pyhf-validation"]
