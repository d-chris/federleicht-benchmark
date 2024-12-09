ARG PYTHON_VERSION=3.13
ARG POETRY_VERSION=1.8.4

# Stage 1: Build the Rust project
FROM rust:latest AS builder

# Install system dependencies and tools
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Build and install agg
WORKDIR /agg
RUN git clone https://github.com/asciinema/agg.git -b v1.5.0 . && \
    cargo build --release

# Stage 2: Build the Python environment
FROM python:${PYTHON_VERSION}-slim AS venv

# Re-declare the ARG variables to make them available in this stage
ARG POETRY_VERSION

RUN pip install poetry==${POETRY_VERSION}

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

COPY . ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry build


# Stage 3: Set up the runtime environment
FROM python:${PYTHON_VERSION}-slim AS runtime

# Specify the author of the Docker image
LABEL org.opencontainers.image.authors="Christoph Dörrer <d-chris@web.de>"


# Install system dependencies and tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    asciinema \
    fonts-dejavu \
    && rm -rf /var/cache/apk/*

# Copy the built binary from the builder stage
COPY --from=builder /agg/target/release/agg /usr/local/bin/

# Copy the wheel file from the build stage
COPY --from=venv /app/dist/*.whl /tmp/

# Set the PIP_CACHE_DIR environment variable
ENV PIP_CACHE_DIR=/tmp/pip_cache

# Install the wheel file and its dependencies using the cache directory
RUN --mount=type=cache,target=$PIP_CACHE_DIR pip install /tmp/*.whl --cache-dir=$PIP_CACHE_DIR

# Set the working directory
WORKDIR /app


ENTRYPOINT ["/bin/sh"]
