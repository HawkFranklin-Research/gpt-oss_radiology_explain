---
title: GPT-OSS - Radiology Explainer Demo
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
# --- ADD GPU HARDWARE ---
hardware: nvidia-t4-small 
app_port: 7860
pinned: false
license: apache-2.0
short_description: Radiology Image & Report Explainer Demo. Built with gpt-oss
models:
  # --- UPDATE THE MODEL ---
  - openai/gpt-oss-20b
secrets:
  - HF_TOKEN
---

# Radiology Image & Report Explainer Demo - Built with gpt-oss

Consider an educational scenario where interacting with a radiology image can
substantially improve learning. This demonstration shows how **gpt-oss** might be built upon to provide a useful tool for exploring radiology images and associated reports by translating them into simple language.

Powered by AI (**gpt-oss-20b**), this space analyzes a sample radiology report and its corresponding Chest X-Ray/CT image. Click on any sentence in the report, and you'll receive an AI-generated explanation tailored to that specific text.

This demonstration is for illustrative purposes only and does not represent a finished or approved product. It is not representative of compliance to any harmonized regulations or standards for quality, safety or efficacy. Any real-world application would require additional development, training, and adaptation. The experience highlighted in this demo shows gpt-oss's baseline capability for the displayed task and is intended to help developers and users explore possible applications and inspire further development.

**Note:** The model runs locally within this Space. Please allow a few minutes for the Space to build and start up if it has been idle.

# Links
* gpt-oss HuggingFace - https://huggingface.co/openai/gpt-oss-120b
* OpenAI Blog - https://openai.com/index/introducing-gpt-oss/
