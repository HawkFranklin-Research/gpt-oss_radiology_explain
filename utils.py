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

import base64
import mimetypes
import logging # Used for logging

logger = logging.getLogger(__name__)

# --- Helper Function for Base64 Encoding ---
def image_to_base64_data_url(image_path):
    """Reads an image file, encodes it to base64, and returns a data URL."""
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            # Fallback or raise error if MIME type can't be guessed
            mime_type = "image/jpeg" # Defaulting to image/jpeg if MIME type detection fails
            logger.warning(f"Could not determine MIME type for {image_path}, defaulting to {mime_type}")

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        logger.error(f"Image file not found at {image_path} for base64 encoding.")
        return None
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}", exc_info=True)
        return None