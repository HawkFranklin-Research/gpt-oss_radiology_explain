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

import os
from pathlib import Path
import csv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Model Configuration ---
HF_TOKEN = os.environ.get("HF_TOKEN", None)
# --- REMOVED: MEDGEMMA_ENDPOINT_URL ---
# MEDGEMMA_ENDPOINT_URL = os.environ.get("MEDGEMMA_ENDPOINT_URL", None)

# --- ADDED: Configuration for local gpt-oss model ---
MODEL_ID = os.environ.get("MODEL_ID", "openai/gpt-oss-20b")
# Path where the model is pre-downloaded in the Dockerfile
MODEL_CACHE_DIR = "/app/models/gpt-oss-20b"


# --- Paths using pathlib ---
BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / 'static'

# --- Load available report/image pairs from CSV (No changes here) ---
AVAILABLE_REPORTS = []
MANIFEST_CSV_PATH = STATIC_DIR / 'reports_manifest.csv'

if MANIFEST_CSV_PATH.is_file():
    try:
        with open(MANIFEST_CSV_PATH, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_headers = {'case_display_name', 'image_path', 'report_path'}
            if not required_headers.issubset(reader.fieldnames):
                logger.error(
                    f"CSV file {MANIFEST_CSV_PATH} is missing one or more required headers: {required_headers - set(reader.fieldnames)}"
                )
            else:
                for row in reader:
                    case_name = row['case_display_name']
                    image_path_from_csv = row['image_path']
                    report_path_from_csv = row['report_path']

                    if not image_path_from_csv:
                        logger.warning(f"Empty image_path in CSV for case '{case_name}'. Skipping this entry.")
                        continue

                    abs_image_path_to_check = BASE_DIR / image_path_from_csv
                    if not abs_image_path_to_check.is_file():
                        logger.warning(f"Image file not found for case '{case_name}' at '{abs_image_path_to_check}'. Skipping this entry.")
                        continue

                    image_file_for_config = image_path_from_csv
                    report_file_for_config = ""

                    if report_path_from_csv:
                        abs_report_path_to_check = BASE_DIR / report_path_from_csv
                        if not abs_report_path_to_check.is_file():
                            logger.warning(
                                f"Report file specified for case '{case_name}' at '{abs_report_path_to_check}' not found. "
                                f"Proceeding without report file for this entry."
                            )
                        else:
                            if report_path_from_csv.startswith('static/'):
                                report_file_for_config = report_path_from_csv
                            else:
                                logger.warning(
                                    f"Report path '{report_path_from_csv}' for case '{case_name}' in CSV "
                                    f"is malformed. Treating as if no report path was specified."
                                )
                    
                    AVAILABLE_REPORTS.append({
                        "name": case_name,
                        "image_file": image_file_for_config,
                        "report_file": report_file_for_config,
                        "image_type": row['image_type']
                    })
        AVAILABLE_REPORTS.sort(key=lambda x: x['name'])
        logger.info(f"Loaded {len(AVAILABLE_REPORTS)} report/image pairs from CSV.")

    except Exception as e:
        logger.error(f"Error reading or processing CSV file {MANIFEST_CSV_PATH}: {e}", exc_info=True)
else:
    logger.warning(f"Manifest CSV file not found at {MANIFEST_CSV_PATH}. AVAILABLE_REPORTS will be empty.")

DEFAULT_REPORT_INFO = AVAILABLE_REPORTS[0] if AVAILABLE_REPORTS else None
