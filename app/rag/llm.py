"""Groq chat-completion client (free tier, OpenAI-compatible Llama models)."""

from __future__ import annotations

from groq import Groq

from app.config import settings

SYSTEM_PROMPT = (
    "You are a precise DevOps and cloud-engineering assistant. Answer the user's "
    "question using ONLY the provided context. If the context does not contain the "
    "answer, say you don't have enough information rather than guessing. Be concise, "
    "use Markdown, and include short code/command examples when helpful."
)


class LLM:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.model = model or settings.groq_model
        self._client = Groq(api_key=api_key or settings.groq_api_key)

    def answer(self, question: str, context: str) -> str:
        user_content = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer using only the context above."
        )
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=700,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return resp.choices[0].message.content or ""
