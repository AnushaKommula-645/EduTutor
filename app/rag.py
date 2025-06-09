import requests
from bs4 import BeautifulSoup
import os
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key="AIzaSyBEmgn35jP1g62GVSfOmhfHBOMki4snsaY")
#genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

def extract_text_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)
        return text
    except Exception as e:
        return f"Error: {e}"

def ask_gemini(question: str, context: str) -> str:
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(f"Context:\n{context}\n\nQuestion:\n{question}")
    return response.text
