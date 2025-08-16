"""Generates a summary of a Youtube video transcript using an LLM."""

import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def summarize_transcript(transcript: str) -> str:
    prompt = f"Please summarize this video. Focus on the main takeaways, summarizing them. Start high level, then go into the details. When participants take specific positions, mention it. As always, keep an eye out for anything unusual or out of the especially notable.\n\n{transcript}\n"

    response = client.chat.completions.create(
        model="openai/gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=16384,
    )

    return response.choices[0].message.content
