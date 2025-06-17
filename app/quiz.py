# app/quiz.py
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_quiz_questions(topic: str = "general knowledge", num_questions: int = 10):
    """
    Generates quiz questions using the Gemini API.
    Attempts to parse the output as JSON for structured questions.
    """
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Crafting the prompt to encourage JSON output for easy parsing
    prompt = f"""
Generate {num_questions} multiple-choice quiz questions about "{topic}".
Each question should have:
1.  A "question" field.
2.  An "options" array with 4 possible answers.
3.  An "answer" field indicating the correct answer from the options.

Format the output as a JSON array of objects.
Example format:
[
  {{
    "question": "What is the capital of France?",
    "options": ["Berlin", "Madrid", "Paris", "Rome"],
    "answer": "Paris"
  }},
  {{
    "question": "Which planet is known as the Red Planet?",
    "options": ["Earth", "Mars", "Jupiter", "Venus"],
    "answer": "Mars"
  }}
]
"""
    try:
        response = model.generate_content(prompt)
        # Attempt to extract text and parse as JSON
        quiz_json_str = response.text.strip()
        # Clean up common markdown artifacts like ```json ... ```
        if quiz_json_str.startswith("```json"):
            quiz_json_str = quiz_json_str[len("```json"):].strip()
        if quiz_json_str.endswith("```"):
            quiz_json_str = quiz_json_str[:-len("```")].strip()
        
        quiz_data = json.loads(quiz_json_str)
        
        # Basic validation for the structure
        if not isinstance(quiz_data, list):
            raise ValueError("Expected a JSON array.")
        for q in quiz_data:
            if not all(k in q for k in ["question", "options", "answer"]):
                raise ValueError("Each question object must have 'question', 'options', 'answer'.")
            if not isinstance(q["options"], list) or len(q["options"]) != 4:
                raise ValueError("Options must be an array of 4 items.")
            if q["answer"] not in q["options"]:
                # If the LLM generates a correct answer not in options, try to pick one from options or flag
                print(f"Warning: Correct answer '{q['answer']}' not found in options for question: {q['question']}")
                # For robustness, you might choose to remove this question or pick a default option
                # For now, we'll let it pass, but it's a potential issue.

        return quiz_data[:num_questions] # Ensure we return max requested questions
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print(f"Raw LLM response (attempted JSON): {quiz_json_str}")
        return {"error": "Could not parse quiz questions from AI. Please try again or refine your prompt. Raw output was not valid JSON."}
    except Exception as e:
        print(f"Error generating quiz questions: {e}")
        return {"error": f"Failed to generate quiz: {str(e)}"}

# Example of how to call it (for testing in quiz.py if needed)
if __name__ == "__main__":
    # Ensure GEMINI_API_KEY is set in your .env file
    questions = generate_quiz_questions(topic="History of India", num_questions=5)
    print(json.dumps(questions, indent=2))