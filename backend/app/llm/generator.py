import json
import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

_DEFAULT_MODEL = "gpt-4o-mini"


def generate_answer(
    prompt: str,
    model: str | None = None,
) -> str:
    """
    Send a prompt to OpenAI chat model and return the response text.
    """

    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        raise ValueError("prompt is required")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    selected_model = model or os.getenv("OPENAI_MODEL") or _DEFAULT_MODEL

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "user",
                    "content": cleaned_prompt,
                }
            ],
        )
    except OpenAIError as error:
        raise RuntimeError(
            f"OpenAI chat request failed: {error}"
        ) from error

    content = _extract_response_text(response)
    if not content:
        raise RuntimeError("Empty response from OpenAI chat model.")

    return content


def generate_suggested_questions(
    context: str,
    model: str | None = None,
) -> List[str]:
    """
    Generate 3 suggested user questions from transcript context.
    """

    cleaned_context = context.strip()
    if not cleaned_context:
        return []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    selected_model = model or os.getenv("OPENAI_MODEL") or _DEFAULT_MODEL

    client = OpenAI(api_key=api_key)

    prompt = (
        "Generate 3 concise questions that can be answered with high confidence "
        "from the transcript excerpt below. Avoid questions that need outside knowledge. "
        "Return ONLY a JSON array of strings. Do not use code fences.\n\n"
        f"Transcript excerpt:\n{cleaned_context}\n"
    )

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
    except OpenAIError as error:
        raise RuntimeError(
            f"OpenAI chat request failed: {error}"
        ) from error

    content = _extract_response_text(response)
    if not content:
        return []

    content = _strip_code_fences(content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = _fallback_parse_questions(content)

    if not isinstance(parsed, list):
        return []

    questions = [str(item).strip() for item in parsed if str(item).strip()]
    cleaned = [q for q in questions if not _looks_like_junk(q)]
    return cleaned[:3]


def _extract_response_text(response) -> str:
    if not response or not response.choices:
        return ""

    message = response.choices[0].message
    if not message or not message.content:
        return ""

    return message.content.strip()


def _fallback_parse_questions(content: str) -> List[str]:
    lines = [line.strip("- ") for line in content.splitlines()]
    return [line for line in lines if line]


def _strip_code_fences(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    return cleaned


def _looks_like_junk(text: str) -> bool:
    lowered = text.lower()
    return lowered in {"json", "[", "]"} or lowered.startswith("```")
