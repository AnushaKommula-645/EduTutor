# from google import genai
# import os
# import json
# from dotenv import load_dotenv

# load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# def generate_quiz_questions(topic: str = "general knowledge", num_questions: int = 10):
#     """
#     Generates quiz questions using the Gemini API (new v2.5 model).
#     """
#     prompt = f"""
# Generate {num_questions} multiple-choice quiz questions about "{topic}".
# Each question should have:
# 1.  A "question" field.
# 2.  An "options" array with 4 possible answers.
# 3.  An "answer" field indicating the correct answer from the options.

# Format the output as a JSON array of objects.
# Example:
# [
#   {{
#     "question": "What is the capital of France?",
#     "options": ["Berlin", "Madrid", "Paris", "Rome"],
#     "answer": "Paris"
#   }}
# ]
# """

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt
#         )

#         quiz_json_str = response.text.strip()
#         if quiz_json_str.startswith("```json"):
#             quiz_json_str = quiz_json_str[7:].strip()
#         if quiz_json_str.endswith("```"):
#             quiz_json_str = quiz_json_str[:-3].strip()

#         quiz_data = json.loads(quiz_json_str)
#         return quiz_data[:num_questions]
#     except json.JSONDecodeError as e:
#         return {"error": "Invalid JSON from AI", "details": str(e)}
#     except Exception as e:
#         return {"error": f"Failed to generate quiz: {str(e)}"}

# if __name__ == "__main__":
#     print(json.dumps(generate_quiz_questions("Artificial Intelligence", 5), indent=2))



from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini client with API key from .env
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_json_block(text: str) -> str:
    """
    Tries to extract a JSON array from the model's raw text output.
    Handles:
    - ```json ... ``` fenced blocks
    - Extra explanation text before/after the JSON
    """
    text = text.strip()

    # Remove ```json fenced code block if present
    if text.startswith("```json"):
        text = text[7:].strip()
    if text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    # If direct JSON parses, use it
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Try to find the first '[' and last ']' (for a JSON array)
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and start < end:
        candidate = text[start: end + 1]
        # Check if this is valid JSON
        json.loads(candidate)  # will raise if invalid
        return candidate

    # If everything fails, raise exception
    raise ValueError("Could not find valid JSON array in model output.")


def generate_quiz_questions(topic: str = "general knowledge", num_questions: int = 10):
    """
    Generates quiz questions using the Gemini 2.5 Flash model.

    Returns:
        - On success: a list of {question, options, answer} objects.
        - On failure: a dict with "error" and "details".
    """
    prompt = f"""
Generate {num_questions} multiple-choice quiz questions about "{topic}".

Each question MUST be a JSON object with:
1. "question": the question text.
2. "options": an array of EXACTLY 4 possible answers.
3. "answer": the correct answer, and it MUST be one of the options.

Return ONLY a valid JSON array of objects. Do NOT include any extra text, comments, or explanation.

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
        # Call Gemini with the same style as your working RAG/chatbot
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        # The Python SDK you're using exposes `.text`, like in your RAG
        raw_text = (getattr(response, "text", None) or "").strip()
        if not raw_text:
            return {"error": "Empty response from Gemini", "details": str(response)}

        quiz_json_str = _extract_json_block(raw_text)
        quiz_data = json.loads(quiz_json_str)

        # Ensure it's a list
        if not isinstance(quiz_data, list):
            return {"error": "Model did not return a JSON array.", "details": quiz_data}

        # Trim to requested number of questions
        return quiz_data[:num_questions]

    except json.JSONDecodeError as e:
        return {"error": "Invalid JSON from AI", "details": str(e)}
    except ValueError as e:
        return {"error": "Failed to extract JSON from AI response", "details": str(e)}
    except Exception as e:
        return {"error": f"Failed to generate quiz: {str(e)}"}


if __name__ == "__main__":
    # Simple manual test
    result = generate_quiz_questions("Artificial Intelligence", 5)
    print(json.dumps(result, indent=2, ensure_ascii=False))
