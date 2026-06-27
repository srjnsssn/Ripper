import json
from abc import ABC, abstractmethod

import fitz

from ..database import engine, sistema_config
from ..vault import vault

SYSTEM_PROMPT = (
    "Analyze this raw PDF text. Find the Table of Contents. "
    "Return ONLY a valid JSON array mapping the chapters: "
    '`[{"title": "...", "start_page": X, "end_page": Y}]`'
)


class BaseAdapter(ABC):
    provider: str

    def extract(self, file_path: str) -> list[dict]:
        api_key = self._fetch_api_key()
        raw_text = self._extract_pdf_text(file_path)
        response = self._call_llm(api_key, raw_text)
        return self._parse_json(response)

    def _fetch_api_key(self) -> str:
        with engine.connect() as conn:
            row = conn.execute(
                sistema_config.select().where(sistema_config.c.id == self.provider)
            ).fetchone()
        if row is None:
            raise RuntimeError(
                f"API key for '{self.provider}' not found in vault. "
                "Save it via POST /api/vault/keys."
            )
        return vault.decrypt(row.valor_cifrado, row.iv, row.tag)

    def _extract_pdf_text(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        pages = [doc[n].get_text() for n in range(min(20, doc.page_count))]
        doc.close()
        return "\n\n--- PAGE BREAK ---\n\n".join(pages)

    def _parse_json(self, content: str | None) -> list[dict]:
        if not content:
            raise RuntimeError(f"{self.provider} returned empty response")
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())

    @abstractmethod
    def _call_llm(self, api_key: str, raw_text: str) -> str:
        ...


class OpenAIAdapter(BaseAdapter):
    provider = "openai"

    def _call_llm(self, api_key: str, raw_text: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_text},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content


class GeminiAdapter(BaseAdapter):
    provider = "gemini"

    def _call_llm(self, api_key: str, raw_text: str) -> str:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(raw_text)
        return response.text


class AnthropicAdapter(BaseAdapter):
    provider = "anthropic"

    def _call_llm(self, api_key: str, raw_text: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_text}],
        )
        return response.content[0].text


class GroqAdapter(BaseAdapter):
    provider = "groq"

    def _call_llm(self, api_key: str, raw_text: str) -> str:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_text},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content


_ADAPTERS: dict[str, type[BaseAdapter]] = {
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "anthropic": AnthropicAdapter,
    "groq": GroqAdapter,
}


def extract_toc_via_ai(file_path: str, provider: str = "gemini") -> list[dict]:
    adapter_cls = _ADAPTERS.get(provider)
    if adapter_cls is None:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Choose from: {', '.join(_ADAPTERS)}"
        )
    return adapter_cls().extract(file_path)
