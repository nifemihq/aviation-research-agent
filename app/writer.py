import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def draft_onepager(query: str, evidence_blocks: list[str]) -> str:
    evidence_text = "\n\n".join(
        [f"Source {i+1}:\n{txt}" for i, txt in enumerate(evidence_blocks)]
    )

    prompt = f"""
You are an academic aviation research assistant.

STRICT RULES:
- Use ONLY the evidence provided.
- If a claim is not in evidence, do not say it.
- If evidence is insufficient, say "Insufficient evidence".
- Do NOT use outside knowledge.

TASK:
Write a one-pager style section answering:
"{query}"

EVIDENCE:
{evidence_text}

OUTPUT FORMAT:
Summary:
(3-5 sentences grounded in evidence)

Key Findings:
- bullet points
- each bullet must end with (Source #)

Limitations:
- what evidence does NOT cover
"""

    # Retry policy: 5 attempts with exponential backoff
    backoff = 2.0
    for attempt in range(1, 6):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            return response.text

        except ClientError as e:
            # 429 = throttled / quota / resource exhausted
            if getattr(e, "status_code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e):
                if attempt == 5:
                    raise
                time.sleep(backoff)
                backoff *= 2
                continue
            raise
