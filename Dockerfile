FROM python:3.10-slim-bullseye
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && \
    rm -rf /var/lib/apt/lists/*
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable \
    && \
    /root/.cargo/bin/rustup default stable \
    && \
    /root/.cargo/bin/cargo install cargo-auditable \
    && \
    rm -rf /root/.rustup /root/.cargo/registry /root/.cargo/git
ENV PATH="/root/.cargo/bin:${PATH}"
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
ENV NLTK_DATA /usr/local/share/nltk_data
RUN python -m nltk.downloader -d ${NLTK_DATA} stopwords wordnet
COPY . /app/
RUN pip install --no-cache-dir . && \
    python ai/email_guard_model.py
EXPOSE 5000
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} backend.app:app