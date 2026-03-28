FROM python:3.12-slim AS base

LABEL maintainer="Tom Sapletta <tom@sapletta.com>"
LABEL org.opencontainers.image.source="https://github.com/semcod/algitex"

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps first (cache layer)
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir -e .

# Additional files
COPY examples/ examples/

# Data volume
RUN mkdir -p /app/data
VOLUME /app/data

ENV ALGITEX_DATA_DIR=/app/data
ENV PROXYM_URL=http://proxym:4000

ENTRYPOINT ["algitex"]
CMD ["--help"]

# ── Test stage ────────────────────────────────────────
FROM base AS test

COPY tests/ tests/
RUN pip install --no-cache-dir pytest
RUN python -m pytest tests/ -v --tb=short

# ── Dev stage ─────────────────────────────────────────
FROM base AS dev

RUN pip install --no-cache-dir pytest ruff mypy
COPY tests/ tests/
CMD ["bash"]
