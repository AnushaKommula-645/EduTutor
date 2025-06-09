import re
from ibm_watsonx_ai.foundation_models import ModelInference

# Use your IBM credentials and model id here (same as your code)
api_key = "S8zKH7B-Pjd0RbxuOgUZc4gJOmPhAq14kMn-jDKc35xe"
project_id = "9554d7f6-08ab-44a4-a5ec-6012e5ca2b2c"
base_url = "https://eu-de.ml.cloud.ibm.com"
model_id = "ibm/granite-3-2b-instruct"

def truncate_prompt(prompt, max_words=1500):
    words = prompt.split()
    if len(words) > max_words:
        return ' '.join(words[-max_words:])
    return prompt

def ask_chatbot(user_input: str) -> str:
    user_prompt = f"""You are a helpful AI assistant. Answer the user's question in detail, providing clear and informative explanations.

User: {user_input}
Assistant:"""
    user_prompt = truncate_prompt(user_prompt, max_words=1500)

    try:
        model = ModelInference(
            model_id=model_id,
            credentials={"apikey": api_key, "url": base_url},
            project_id=project_id
        )

        response = model.generate_text(
            prompt=user_prompt,
            params={
                "max_new_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
                "decoding_method": "sample",
                "stop_sequences": ["<|endoftext|>", "User:"]
            }
        )
        bot_response = response['generated_text'] if isinstance(response, dict) and 'generated_text' in response else str(response)
        bot_response = re.split(r'\bUser:|\bAssistant:', bot_response)[0].strip()
        return bot_response
    except Exception as e:
        return f"Error: {str(e)}"
