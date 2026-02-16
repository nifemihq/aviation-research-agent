import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


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

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text

# for m in client.models.list():
#     print(m.name)
