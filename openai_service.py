import json
import os
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment variables")

# Configure OpenAI client for OpenRouter
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY,
) if OPENAI_API_KEY else None

def generate_question_variations(base_question, topic_name, difficulty, category, num_variations=5):
    """
    Generate multiple variations of a lab question using OpenAI API.
    Each variation should be unique but equivalent in difficulty and concept.
    """
    if not openai_client:
        raise Exception("OpenAI API key not configured")
    
    try:
        prompt = f"""
        You are an expert lab instructor creating variations of laboratory questions for students.
        
        Topic: {topic_name}
        Category: {category}
        Difficulty: {difficulty}
        Base Question: {base_question}
        
        Generate {num_variations} unique but equivalent laboratory questions based on the base question above.
        Each question should:
        1. Test the same core concept and skills
        2. Have the same difficulty level ({difficulty})
        3. Be completely unique in wording and specific details
        4. Be suitable for a laboratory setting
        5. Include a brief expected answer or approach
        
        Respond with a JSON object containing an array of question variations.
        Format: {{"variations": [{{"question": "question text", "expected_answer": "brief expected answer"}}, ...]}}
        """
        
        response = openai_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert laboratory instructor specializing in creating fair and equivalent question variations for student assessments."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from OpenAI API")
        result = json.loads(content)
        variations = result.get("variations", [])
        
        if len(variations) < num_variations:
            logging.warning(f"Requested {num_variations} variations but only got {len(variations)}")
        
        logging.info(f"Successfully generated {len(variations)} question variations for topic: {topic_name}")
        return variations
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse OpenAI response as JSON: {e}")
        raise Exception("Failed to parse AI response. Please try again.")
    
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        raise Exception(f"Failed to generate questions: {str(e)}")

def validate_question_quality(question_text, topic_name, difficulty):
    """
    Use OpenAI to validate if a generated question meets quality standards.
    """
    if not openai_client:
        return True  # Skip validation if OpenAI not available
    
    try:
        prompt = f"""
        Evaluate this laboratory question for quality and appropriateness:
        
        Topic: {topic_name}
        Difficulty: {difficulty}
        Question: {question_text}
        
        Assess the question on:
        1. Clarity and understandability
        2. Appropriate difficulty level
        3. Relevance to the topic
        4. Suitability for laboratory setting
        
        Respond with JSON: {{"valid": true/false, "feedback": "brief explanation"}}
        """
        
        response = openai_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quality assurance expert for educational content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("Empty response from OpenAI API")
        result = json.loads(content)
        return result.get("valid", True)
        
    except Exception as e:
        logging.error(f"Question validation error: {e}")
        return True  # Default to valid if validation fails
