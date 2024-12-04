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

# Stage 2: Set up the Python environment
FROM python:3.13-slim

# Specify the author of the Docker image
LABEL org.opencontainers.image.authors="Christoph Dörrer <d-chris@web.de>"

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and tools
RUN apt-get update && apt-get install -y \
    # curl \
    # wget \
    fish \
    asciinema \
    ffmpeg

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the built binary from the builder stage
COPY --from=builder /agg/target/release/agg /usr/local/bin/

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set working directory
WORKDIR /app

# Copy only the poetry files first to take advantage of caching
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (this will be cached unless pyproject.toml or poetry.lock changes)
RUN poetry install --no-cache

# Now copy the rest of the application files (this will be cached separately)
COPY . /app


# Set the default command to use poetry shell
# ENTRYPOINT ["/bin/bash", "-c", "poetry shell && exec bash"]
# ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "fish" ]