import os
import re
import time
from typing import List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.8-flash"


class QnAItem(BaseModel):
    question: str
    answer: str


class QnAResponse(BaseModel):
    english: List[QnAItem]
    hindi: List[QnAItem]
    marathi: List[QnAItem]


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text: str, max_chars: int = 12000) -> List[str]:
    text = clean_text(text)

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current) + len(paragraph) + 2 <= max_chars:
            current += paragraph + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())

            current = paragraph + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def normalize_question(question: str) -> str:
    question = question.lower().strip()
    question = re.sub(r"\s+", " ", question)
    question = re.sub(r"[^\w\s]", "", question)
    return question


def remove_duplicates(
    items: List[QnAItem],
    limit: int
) -> List[QnAItem]:

    seen = set()
    result = []

    for item in items:

        question = item.question.strip()
        answer = item.answer.strip()

        if not question or not answer:
            continue

        key = normalize_question(question)

        if key in seen:
            continue

        seen.add(key)

        result.append(
            QnAItem(
                question=question,
                answer=answer
            )
        )

        if len(result) >= limit:
            break

    return result


def generate_for_chunk(
    client,
    text: str,
    number_of_questions: int
) -> QnAResponse:

    prompt = f"""
You are a multilingual Question-Answer generation system.

Read ONLY the source text below.

SOURCE TEXT:
{text}

Generate {number_of_questions} QnA pairs in each of these languages:

1. English
2. Hindi
3. Marathi

Rules:

- Questions and answers must use ONLY information from the source.
- Do not add outside knowledge.
- Do not invent facts.
- Questions must be meaningful and context-aware.
- Answers must be directly supported by the source.
- Avoid duplicate questions.
- English must be in English.
- Hindi must use Devanagari.
- Marathi must use Devanagari.
- Keep answers concise but informative.
- All three languages should cover equivalent information.
- Return only the requested structured QnA response.
"""

    last_error = None

    for attempt in range(4):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": QnAResponse,
                },
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return QnAResponse.model_validate_json(
                response.text
            )

        except Exception as e:

            last_error = e
            error_text = str(e)

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text
                or "429" in error_text
            ):

                if attempt < 3:
                    wait_time = 5 * (attempt + 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)
                    continue

            raise

    raise RuntimeError(
        f"Gemini request failed after retries: {last_error}"
    )


def generate_multilingual_qna(
    text: str,
    num_qna: int = 10
) -> QnAResponse:

    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Please check your .env file."
        )

    if not text or not text.strip():
        raise ValueError(
            "No text was extracted from the document."
        )

    if num_qna < 1:
        raise ValueError(
            "Number of QnA pairs must be at least 1."
        )

    client = genai.Client(
        api_key=API_KEY
    )

    chunks = split_into_chunks(text)

    if not chunks:
        raise ValueError(
            "Could not create document chunks."
        )

    english = []
    hindi = []
    marathi = []

    questions_per_chunk = max(
        2,
        (num_qna + len(chunks) - 1) // len(chunks)
    )

    for chunk in chunks:

        result = generate_for_chunk(
            client=client,
            text=chunk,
            number_of_questions=questions_per_chunk
        )

        english.extend(result.english)
        hindi.extend(result.hindi)
        marathi.extend(result.marathi)

    english = remove_duplicates(
        english,
        num_qna
    )

    hindi = remove_duplicates(
        hindi,
        num_qna
    )

    marathi = remove_duplicates(
        marathi,
        num_qna
    )

    if not english:
        raise RuntimeError(
            "No English QnA pairs were generated."
        )

    if not hindi:
        raise RuntimeError(
            "No Hindi QnA pairs were generated."
        )

    if not marathi:
        raise RuntimeError(
            "No Marathi QnA pairs were generated."
        )

    return QnAResponse(
        english=english,
        hindi=hindi,
        marathi=marathi
    )