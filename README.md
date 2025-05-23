---
title: MedGemma - Radiology Explainer Demo
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: Radiology Image & Report Explainer Demo. Built with MedGemma
models:
  - google/medgemma-4b-it
secrets:
  - HF_TOKEN
---

# Radiology Image & Report Explainer Demo - Built with MedGemma

Consider an educational scenario where interacting with a radiology image can
substantially improve learning. This demonstration shows how MedGemma might be built upon to provide a useful tool for exploring radiology images and associated reports by translating them into simple language, with visual cues to highlight the relevant areas of the image.

Powered by AI (MedGemma-4B Multimodel), this space analyzes both a sample radiology report and its corresponding Chest X-Ray/CT image. Click on any sentence in the report, and you'll receive an AI-generated explanation tailored to that specific text and visual context. When relevant, the explanation will also pinpoint the corresponding area on the X-ray/CT image.

This demonstration is for illustrative purposes only and does not represent a finished or approved product. It is not representative of compliance to any harmonized regulations or standards for quality, safety or efficacy. Any real-world application would require additional development, training, and adaptation. The experience highlighted in this demo shows MedGemma's baseline capability for the displayed task and is intended to help developers and users explore possible applications and inspire further development.

**Note:** This space uses a HuggingFace endpoint that may scale down to zero due to inactivity. If this occurs, please allow approximately 10 minutes for the endpoint to restart. As an alternative, the model can be deployed on ModelGarden (see the link below). 

# Links
* MedGemma HuggingFace - https://huggingface.co/collections/google/medgemma-release-680aade845f90bec6a3f60c4
* MedGemma DevSite - https://developers.google.com/health-ai-developer-foundations/medgemma
* MedGemma ModelGarden - https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/medgemma
* HAI-DEF models - https://developers.google.com/health-ai-developer-foundations
