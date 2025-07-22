# backend/Dockerfile
# Use a lightweight Python 3.10 image based on Debian Buster for consistency and compatibility
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies:
# - build-essential: General compilation tools (e.g., for C/C++ extensions)
# - curl: Needed to download the Rust installer
# Clean up apt lists to keep the image size down
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && \
    rm -rf /var/lib/apt/lists/*

# Install Rust compiler and Cargo (required by Python packages like 'tokenizers')
# This uses rustup, the recommended installer for Rust.
# Ensure that if the build environment has specific user IDs, rustup installs for the correct one.
# For 'root' user (default in Docker), this path is fine.
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable \
    && \
    /root/.cargo/bin/rustup default stable \
    && \
    # Optional: Install cargo-auditable if you need audited builds, otherwise it can be removed
    /root/.cargo/bin/cargo install cargo-auditable \
    && \
    # Clean up Rust installation files to reduce image size
    rm -rf /root/.rustup /root/.cargo/registry /root/.cargo/git

# Add Rust's binary directory to the system PATH for subsequent commands (e.g., pip builds)
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy backend requirements.txt and install Python dependencies
# This step is placed early to leverage Docker layer caching.
# If only your application code changes, this layer won't be rebuilt.
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set NLTK_DATA environment variable and download necessary NLTK data.
# This ensures NLTK finds its data when your AI model's preprocessing runs.
ENV NLTK_DATA /usr/local/share/nltk_data
RUN python -m nltk.downloader -d ${NLTK_DATA} stopwords wordnet

# Copy the entire project for SDK installation and model training.
# This includes ai/, email_guard_sdk/, setup.py, README.md, data/, backend/
COPY . /app/

# Install the email_guard_sdk package (from the current working directory)
# and then run the model training script.
# This ensures the model is generated based on the code in the current build.
RUN pip install --no-cache-dir . && \
    python ai/email_guard_model.py

# Expose the port that Gunicorn will listen on.
# While it's 5000 by default, hosting platforms will use their own designated port.
EXPOSE 5000

# Command to run the application using Gunicorn.
# It binds to all network interfaces (0.0.0.0) and uses the $PORT environment variable
# provided by the hosting platform (e.g., Railway, Render), defaulting to 5000 if not set.
# 'backend.app:app' refers to the 'app' object within the 'app.py' file inside the 'backend' directory.
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "backend.app:app"]