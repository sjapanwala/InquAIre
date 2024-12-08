import os
from dotenv import load_dotenv
# pip install python-dotenv

import google.generativeai as genai
# pip install -q -U google-generativeai

load_dotenv()

# https://ai.google.dev/tutorials/python_quickstart

class GeminiAI:
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY")

        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(self, input_text):
        """Generates a response using Gemini model"""
        response = self.model.generate_content(input_text)
        return response