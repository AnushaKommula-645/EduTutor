# import re
# from ibm_watsonx_ai.foundation_models import ModelInference
# from dotenv import load_dotenv
# import os

# load_dotenv()  # Loads variables from .env

# api_key = os.getenv("IBMs_API_KEY")
# project_id = os.getenv("IBM_PROJECT_ID")
# base_url = os.getenv("IBM_BASE_URL")
# model_id = os.getenv("IBM_MODEL_ID")

# print("IBM_API_KEY:", api_key)
# print("IBM_PROJECT_ID:", project_id)
# print("IBM_BASE_URL:", base_url)
# print("IBM_MODEL_ID:", model_id)

# # Use your IBM credentials and model id here (same as your code)
# # api_key = "S8zKH7B-Pjd0RbxuOgUZc4gJOmPhAq14kMn-jDKc35xe"
# # project_id = "9554d7f6-08ab-44a4-a5ec-6012e5ca2b2c"
# # base_url = "https://eu-de.ml.cloud.ibm.com"
# # model_id = "ibm/granite-3-2b-instruct"

# def truncate_prompt(prompt, max_words=1500):
#     words = prompt.split()
#     if len(words) > max_words:
#         return ' '.join(words[-max_words:])
#     return prompt
# # def is_educational_question(user_input: str) -> bool:
# #     # Simple keyword check — can be replaced with NLP classification
# #     keywords = ["study", "homework", "exam", "math", "science", "history", "biology", "notes", "assignment", "class", "school"]
# #     return any(kw.lower() in user_input.lower() for kw in keywords)

# def ask_chatbot(user_input: str) -> str:
#     # if not is_educational_question(user_input):
#     #     return "I'm here to help with your studies. Please ask an education-related question."
    
#     user_prompt = f"""
# You are EduTutor, an AI assistant that only helps with education-related topics such as school subjects, studying, homework, exams, learning tips, and academic tools. 

# Do not answer questions unrelated to education (like travel, food, entertainment, health, etc.). If the user asks something outside your scope, respond with:
# "I'm here to help with your studies. Please ask an education-related question."

# User: {user_input}
# EduTutor:"""

#     user_prompt = truncate_prompt(user_prompt, max_words=1500)

#     try:
#         model = ModelInference(
#             model_id=model_id,
#             credentials={"apikey": api_key, "url": base_url},
#             project_id=project_id
#         )

#         response = model.generate_text(
#             prompt=user_prompt,
#             params={
#                 "max_new_tokens": 300,
#                 "temperature": 0.7,
#                 "top_p": 0.9,
#                 "decoding_method": "sample",
#                 "stop_sequences": ["<|endoftext|>", "User:"]
#             }
#         )
#         bot_response = response['generated_text'] if isinstance(response, dict) and 'generated_text' in response else str(response)
#         bot_response = re.split(r'\bUser:|\bAssistant:', bot_response)[0].strip()
#         return bot_response
#     except Exception as e:
#         return f"Error: {str(e)}"


import re
from ibm_watsonx_ai.foundation_models import ModelInference
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

api_key = os.getenv("IBMs_API_KEY")
project_id = os.getenv("IBM_PROJECT_ID")
base_url = os.getenv("IBM_BASE_URL")
model_id = os.getenv("IBM_MODEL_ID")  # e.g. ibm/granite-3-3-8b-instruct


def truncate_prompt(prompt, max_words=1500):
    words = prompt.split()
    if len(words) > max_words:
        return " ".join(words[-max_words:])
    return prompt


def ask_chatbot(user_input: str) -> str:
    user_prompt = f"""
You are EduTutor, an AI assistant that only helps with education-related topics such as school subjects,
studying, homework, exams, learning tips, and academic tools.

Do not answer questions unrelated to education (like travel, food, entertainment, health, etc.).
If the user asks something outside your scope, respond with:
"I'm here to help with your studies. Please ask an education-related question."

User: {user_input}
EduTutor:
"""

    user_prompt = truncate_prompt(user_prompt, max_words=1500)

    try:
        model = ModelInference(
            model_id=model_id,
            credentials={"apikey": api_key, "url": base_url},
            project_id=project_id,
        )

        response = model.generate_text(
            prompt=user_prompt,
            params={
                "max_new_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
                "decoding_method": "sample",
                "stop_sequences": ["<|endoftext|>", "User:"],
            },
        )

        # Handle both possible formats: dict or plain string
        if isinstance(response, dict):
            # Newer SDKs often use this key
            if "generated_text" in response:
                bot_response = response["generated_text"]
            # Older style: results[0].generated_text
            elif "results" in response and response["results"]:
                bot_response = response["results"][0].get("generated_text", "")
            else:
                bot_response = str(response)
        else:
            # If it's already a string
            bot_response = str(response)

        # Remove any extra continuation after "User:" or "Assistant:"
        bot_response = re.split(r"\bUser:|\bAssistant:", bot_response)[0].strip()

        if not bot_response:
            bot_response = "Sorry, I couldn't generate a response. Please try again."

        return bot_response

    except Exception as e:
        return f"Error: {str(e)}"
