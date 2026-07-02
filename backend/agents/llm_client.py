from google import genai
from pydantic import BaseModel
from typing import Type, TypeVar
from backend.core.config import settings

T = TypeVar('T', bound=BaseModel)

# We initialize the client when needed to allow testing without key
def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text

def generate_json(prompt: str, response_schema: Type[T], model: str = "gemini-2.5-flash") -> T:
    client = get_gemini_client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': response_schema
        }
    )
    return response_schema.model_validate_json(response.text)
