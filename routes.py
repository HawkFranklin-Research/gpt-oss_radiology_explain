import logging
from flask import Blueprint, render_template, request, jsonify
from pathlib import Path
import json

import os
import config
import utils
from llm_client import generate_completion_stream, is_initialized as llm_is_initialized
from cache_store import cache

# --- Import Harmony modules ---
from openai_harmony import (
    SystemContent,
    Message,
    Conversation,
    Role,
    load_harmony_encoding,
    HarmonyEncodingName,
)

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# --- Serve the index and report details (No changes needed for these routes) ---
@main_bp.route('/')
def index():
    if not config.AVAILABLE_REPORTS:
        logger.warning("No reports found in config. AVAILABLE_REPORTS is empty.")
    return render_template('index.html', available_reports=config.AVAILABLE_REPORTS)

@main_bp.route('/get_report_details/<report_name>')
def get_report_details(report_name):
    selected_report_info = next((item for item in config.AVAILABLE_REPORTS if item['name'] == report_name), None)
    if not selected_report_info:
        return jsonify({"error": f"Report '{report_name}' not found."}), 404
    
    report_file = selected_report_info.get('report_file')
    image_file = selected_report_info.get('image_file')
    report_text_content = ""
    
    if report_file:
        try:
            actual_server_report_path = config.BASE_DIR / report_file
            report_text_content = actual_server_report_path.read_text(encoding='utf-8').strip()
        except Exception as e:
            logger.error(f"Error reading report file: {e}", exc_info=True)
            return jsonify({"error": "Error reading report file."}), 500
            
    image_type_from_config = selected_report_info.get('image_type')
    display_image_type = 'Chest X-Ray' if image_type_from_config == 'CXR' else 'CT'
    return jsonify({"text": report_text_content, "image_file": image_file, "image_type": display_image_type})

# --- MAJOR CHANGES in the /explain route ---
@main_bp.route('/explain', methods=['POST'])
def explain_sentence():
    """Handles the explanation request using the local gpt-oss model."""
    if not llm_is_initialized():
        logger.error("LLM client not initialized. Cannot process request.")
        return jsonify({"error": "LLM client not initialized on the server."}), 500

    data = request.get_json()
    if not data or 'sentence' not in data or 'report_name' not in data:
        return jsonify({"error": "Missing 'sentence' or 'report_name' in request"}), 400

    selected_sentence = data['sentence']
    report_name = data['report_name']
    logger.info(f"Received request to explain: '{selected_sentence}' for report: '{report_name}'")

    selected_report_info = next((item for item in config.AVAILABLE_REPORTS if item['name'] == report_name), None)
    if not selected_report_info:
        return jsonify({"error": f"Report '{report_name}' not found."}), 404

    # Note: We are no longer sending the image to the model, as gpt-oss (via transformers)
    # does not support multimodal input in this way. The prompt still provides the context.
    report_file = selected_report_info.get('report_file')
    image_type = selected_report_info.get('image_type')

    cache_key = f"gpt-oss-explain::{report_name}::{selected_sentence}"
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info("Returning cached explanation.")
        return jsonify({"explanation": cached_result})

    full_report_text = ""
    if report_file:
        try:
            server_report_path = config.BASE_DIR / report_file
            full_report_text = server_report_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading report file {server_report_path}: {e}", exc_info=True)
            return jsonify({"error": "Error reading report file."}), 500

    # --- Construct Harmony Prompt ---
    system_prompt = (
        "You are a public-facing clinician. "
        f"A learning user has provided a sentence from a radiology report and is viewing the accompanying {image_type} image. "
        "Your task is to explain the meaning of ONLY the provided sentence in simple, clear terms. Explain terminology and abbreviations. Keep it concise. "
        "Directly address the meaning of the sentence. Do not use introductory phrases like 'Okay' or refer to the sentence itself (e.g., 'This sentence means...'). "
        f"{f'Since the user is looking at their {image_type} image, provide guidance on where to look, if applicable. ' if image_type != 'CT' else ''}"
        "Do not discuss any other part of the report. Stick to facts in the text. Do not infer anything. \n"
        "===\n"
        f"For context, the full REPORT is:\n{full_report_text}"
    )
    user_prompt_text = f"Explain this sentence from the radiology report: '{selected_sentence}'"
    
    try:
        # 1. Load the Harmony encoding for gpt-oss
        encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

        # 2. Create Harmony message objects
        system_content = SystemContent.new().with_model_identity(system_prompt)
        system_message = Message.from_role_and_content(Role.SYSTEM, system_content)
        user_message = Message.from_role_and_content(Role.USER, user_prompt_text)

        # 3. Create the conversation
        conversation = Conversation.from_messages([system_message, user_message])
        
        # 4. Render the conversation to token IDs for the model
        input_ids = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

        logger.info("Sending request to local gpt-oss model...")
        
        # 5. Call the new local generation function
        explanation = generate_completion_stream(
            input_ids,
            max_new_tokens=250,
            temperature=0.0
        )
        explanation = explanation.strip()

        if explanation:
            cache.set(cache_key, explanation, expire=None)

        logger.info("Explanation generated successfully.")
        return jsonify({"explanation": explanation or "No explanation content received from the model."})

    except Exception as e:
        logger.error(f"Error during local model inference: {e}", exc_info=True)
        user_error_message = ("Failed to generate explanation. The service might be experiencing issues. Please try again.")
        return jsonify({"error": user_error_message}), 500
