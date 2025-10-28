from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_quiz_questions(topic: str = "general knowledge", num_questions: int = 10):
    """
    Generates quiz questions using the Gemini API (new v2.5 model).
    """
    prompt = f"""
Generate {num_questions} multiple-choice quiz questions about "{topic}".
Each question should have:
1.  A "question" field.
2.  An "options" array with 4 possible answers.
3.  An "answer" field indicating the correct answer from the options.

Format the output as a JSON array of objects.
Example:
[
  {{
    "question": "What is the capital of France?",
    "options": ["Berlin", "Madrid", "Paris", "Rome"],
    "answer": "Paris"
  }}
]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        quiz_json_str = response.text.strip()
        if quiz_json_str.startswith("```json"):
            quiz_json_str = quiz_json_str[7:].strip()
        if quiz_json_str.endswith("```"):
            quiz_json_str = quiz_json_str[:-3].strip()

        quiz_data = json.loads(quiz_json_str)
        return quiz_data[:num_questions]
    except json.JSONDecodeError as e:
        return {"error": "Invalid JSON from AI", "details": str(e)}
    except Exception as e:
        return {"error": f"Failed to generate quiz: {str(e)}"}

if __name__ == "__main__":
    print(json.dumps(generate_quiz_questions("Artificial Intelligence", 5), indent=2))
