import requests
from bs4 import BeautifulSoup
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_url(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 40]
        text = ' '.join(paragraphs)
        return text[:4000] if len(text) > 4000 else text
    except Exception as e:
        return f"Error extracting text: {e}"

def ask_gemini(question: str, context: str) -> str:
    try:
        prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"
