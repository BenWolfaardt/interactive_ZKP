FROM python:3.11.4-slim

COPY config /app/config
COPY proto /app/proto
COPY src /app/src
COPY docker-compose.yml /app
COPY pyproject.toml /app
COPY README.md /app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY ["ci/server/docker-entrypoint.sh", "/usr/local/bin/docker-entrypoint.sh"]
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
