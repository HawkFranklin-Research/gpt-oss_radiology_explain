#!/bin/bash
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

set -e
APP_NAME="radiology-report-explain"
HOST_APP_DIR="$(pwd)"
CONTAINER_APP_DIR="/app"

docker rm $APP_NAME || true

# Build the Docker image
echo "Building Docker image..."
docker build -t radiology-report-explain .

# Check if the build was successful
if [ $? -ne 0 ]; then
  echo "Docker build failed!"
  exit 1
fi

# Run the Docker container with a volume
echo "Running Docker container with volume (attached)..."
docker run \
  -p 7860:7860 \
  --env-file env.list \
  --name "$APP_NAME" \
  -v "$HOST_APP_DIR:$CONTAINER_APP_DIR" \
  -u $(id -u):$(id -g) \
  radiology-report-explain

# The script will block here, showing the container's output.
# To stop the container, press Ctrl+C in this terminal.

# The following code will only run after the container exits (e.g., Ctrl+C)
echo "Docker container has exited."
echo "To remove the container, run: docker rm $APP_NAME"
