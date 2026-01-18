import os
import time
from openai import OpenAI

from app.logger import get_logger

log = get_logger()


def analyze_resume(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in your .env file.")

    client = OpenAI(api_key=api_key)

    try:
        model = "gpt-4o-mini"
        prompt_chars = len(prompt)

        log.info("openai_request_start | model=%s | prompt_chars=%d | temperature=%.2f | max_tokens=%d",model,prompt_chars,temperature,max_tokens,)

        start = time.perf_counter()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume reviewer with years of experience in HR and recruitment.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        duration_ms = int((time.perf_counter() - start) * 1000)

        log.info("openai_request_end | model=%s | duration_ms=%d", model, duration_ms)

        usage = getattr(response, "usage", None)
        if usage:
            log.info(
                "openai_usage | prompt_tokens=%s | completion_tokens=%s | total_tokens=%s",
                getattr(usage, "prompt_tokens", None),
                getattr(usage, "completion_tokens", None),
                getattr(usage, "total_tokens", None),
            )

        return response.choices[0].message.content

    except Exception:
        log.exception("openai_request_failed")
        raise
