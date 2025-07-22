# Dockerfile (now at the root of your EMAIL_GUARD repository)
FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies (build-essential, curl)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Rust compiler and Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable \
    && /root/.cargo/bin/rustup default stable \
    && /root/.cargo/bin/cargo install cargo-auditable \
    && rm -rf /root/.rustup /root/.cargo/registry /root/.cargo/git
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy backend requirements.txt and install Python dependencies
# Path is now relative to the repo root
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set NLTK_DATA environment variable and download necessary NLTK data
ENV NLTK_DATA /usr/local/share/nltk_data
RUN python -m nltk.downloader -d ${NLTK_DATA} stopwords wordnet

# Copy the entire project (from repo root to /app)
# This copies ai/, backend/, data/, email_guard_sdk/, setup.py, README.md
COPY . /app/

# Install the SDK and train the model during the build process
RUN pip install --no-cache-dir . && \
    python ai/email_guard_model.py

EXPOSE 5000
# CMD command remains the same
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "backend.app:app"]