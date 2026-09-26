import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a structured evidence extraction system for an online-fraud incident organizer.
Extract only information explicitly supported by the supplied evidence. Never invent values.
Return JSON only. Use null for unavailable scalar fields and [] for unavailable arrays.
Do not decide whether fraud legally occurred. The fields explicit_fields and inferred_fields
must describe provenance: put only directly stated facts in explicit_fields; use inferred_fields
only for cautious contextual interpretations such as payment_method inferred from the phrase 'UPI'.
Schema:
{
  \"amount\": number|null,
  \"currency\": string|null,
  \"payment_method\": string|null,
  \"recipient\": {\"type\": string|null, \"value\": string|null},
  \"date\": string|null,
  \"time\": string|null,
  \"transaction_id\": string|null,
  \"sender\": string|null,
  \"explicit_fields\": string[],
  \"inferred_fields\": string[]
}
"""


def llm_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


async def extract_with_llm(text: str) -> dict[str, Any] | None:
    if not llm_available():
        return None

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = await client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)
