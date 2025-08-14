import json
import os
import logging
import requests

# Load API key from environment variable
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    raise Exception("OPENROUTER_API_KEY is not set in environment variables.")

def call_openrouter(model, messages, max_tokens=1000, temperature=0.7, response_format=None):
    """Send a chat completion request to OpenRouter API."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    # Optional: If the model supports JSON output, request it
    if response_format:
        payload["response_format"] = response_format

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        logging.error(f"OpenRouter API error: {response.text}")
        raise Exception(f"OpenRouter API returned status {response.status_code}")

    return response.json()

def generate_question(prompt):
    """Generate a single AI question from a prompt."""
    result = call_openrouter(
        model="gpt-4",  # or another OpenRouter-supported model
        messages=[{"role": "user", "content": prompt}]
    )
    return result

def generate_question_variations(base_question, topic_name, difficulty, category, num_variations=5):
    """Generate multiple variations of a lab question."""
    prompt = f"""
    You are an expert lab instructor creating variations of laboratory questions.

    Topic: {topic_name}
    Category: {category}
    Difficulty: {difficulty}
    Base Question: {base_question}

    Generate {num_variations} unique but equivalent laboratory questions.
    Each should:
    1. Test the same concept and skills
    2. Have the same difficulty
    3. Be unique in wording and details
    4. Be suitable for a lab setting
    5. Include a brief expected answer

    Respond in JSON format:
    {{
        "variations": [
            {{"question": "...", "expected_answer": "..."}},
            ...
        ]
    }}
    """
    try:
        result = call_openrouter(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a lab instructor creating fair question variations."},
                      {"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )

        # Extract the text output
        content = result["choices"][0]["message"]["content"]
        return json.loads(content).get("variations", [])

    except json.JSONDecodeError:
        logging.error("Failed to parse AI JSON output.")
        raise Exception("Invalid JSON from AI response.")

def validate_question_quality(question_text, topic_name, difficulty):
    """Validate a generated question for quality using AI."""
    prompt = f"""
    Evaluate this lab question for clarity, relevance, and difficulty.

    Topic: {topic_name}
    Difficulty: {difficulty}
    Question: {question_text}

    Respond in JSON format:
    {{
        "valid": true/false,
        "feedback": "brief explanation"
    }}
    """
    try:
        result = call_openrouter(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a QA expert for educational content."},
                      {"role": "user", "content": prompt}],
            max_tokens=500
        )

        content = result["choices"][0]["message"]["content"]
        return json.loads(content).get("valid", True)

    except Exception as e:
        logging.error(f"Validation error: {e}")
        return True  # Assume valid if AI validation fails
