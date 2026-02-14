"""Generates a summary of a Youtube video transcript using an LLM."""

from openai import OpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE

client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
)

def summarize_transcript(transcript: str) -> str:
    prompt = f"Please summarize this video. Focus on the main takeaways, summarizing them. Start high level, then go into the details. When participants take specific positions, mention it. As always, keep an eye out for anything unusual or out of the especially notable.\n\n{transcript}\n"

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )

    return response.choices[0].message.content
