# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --- Use Python 3.12 as required by gpt-oss ---
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV CACHE_DIR=/data/cache
# --- Define a build argument for the Hugging Face token ---
ARG HF_TOKEN

# Install system dependencies
RUN apt-get update && \
    apt-get install -y fonts-ocr-a fonts-ocr-b unzip --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set up a new user
RUN useradd -m -s /bin/bash -u 1000 user

WORKDIR /app

# Install pip dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Pre-download the model during the build process ---
# This uses the build argument for authentication.
# The Space secret HF_TOKEN will be passed during the build on the Hub.
RUN huggingface-cli download openai/gpt-oss-20b --local-dir /app/models/gpt-oss-20b --token $HF_TOKEN

# Copy the rest of the application code
COPY --chown=user:user . .

# Run tests
RUN python -m unittest discover tests

# Prepare cache directory
RUN mkdir -p $CACHE_DIR && \
    chmod -R 777 $CACHE_DIR && \
    unzip -o ./default_cache/radexplain-cache.zip -d $CACHE_DIR

USER user

EXPOSE 7860

CMD ["gunicorn", \
     "--bind", "0.0.0.0:7860", \
     "--timeout", "600", \
     "--worker-class", "gthread", \
     "--workers", "1", \
     "--threads", "4", \
     "--preload", \
     "app:app"]
