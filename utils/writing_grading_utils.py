import openai
import environ
from django.conf import settings
from utils.cache_manager import fallback_cache
import json
import logging

logger = logging.getLogger(__name__)

env = environ.Env()
environ.Env.read_env("LingoBoard/.env")

OPENAI_API_KEY = env("OPENAI_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

prompt_criteria = ""
with open("utils/writing_grade_criteria.txt", "r") as criteria_file:
    prompt_criteria = criteria_file.read()


def grade_input_text(input) -> dict:
    # Create a cache key based on the input text
    cache_key = f"writing_grade_{hash(input)}"

    # Try to get cached result first
    cached_result = fallback_cache.get(cache_key)
    if cached_result:
        return cached_result

    prompt = f"""
    {prompt_criteria}

    Answer:
    \"\"\"{input}\"\"\"

    Return your response in JSON format like:
    {{
        "score": 7,
        "feedback": "Well-structured, but lacks evidence."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4096,
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON safely
        try:
            result = json.loads(content)
            # Cache the result for 1 hour
            fallback_cache.set(cache_key, result, 3600)
            return result
        except json.JSONDecodeError:
            result = {
                "score": None,
                "feedback": f"Could not parse model output: {content}",
            }
            # Cache error results for shorter time (15 minutes)
            fallback_cache.set(cache_key, result, 900)
            return result

    except Exception as e:
        result = {"score": None, "feedback": f"OpenAI error: {str(e)}"}
        # Cache error results for shorter time (15 minutes)
        fallback_cache.set(cache_key, result, 900)
        return result
