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

FROM python:3.10-slim

# Set an environment variable for unbuffered python output (good for logging)
# and define the cache directory path
ENV PYTHONUNBUFFERED=1
ENV CACHE_DIR=/data/cache

# Install system dependencies first, as they change less frequently
RUN apt-get update && \
    apt-get install -y fonts-ocr-a fonts-ocr-b unzip --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
# -m creates the home directory /home/user
# -s /bin/bash sets a default shell (good practice for debugging or execing into the container)
RUN useradd -m -s /bin/bash -u 1000 user

WORKDIR /app

COPY --chown=user:user . .

RUN pip install --no-cache-dir -r requirements.txt

# Run tests after installing dependencies
RUN python -m unittest discover tests

RUN mkdir -p $CACHE_DIR
RUN chmod -R 777 $CACHE_DIR
RUN unzip -o ./default_cache/radexplain-cache.zip -d $CACHE_DIR

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
