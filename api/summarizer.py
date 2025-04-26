"""Generates a summary of a Youtube video transcript using an LLM."""

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

vertexai.init(project='elegant-gearing-417520', location='us-central1')

#gemini_model = GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
gemini_model = GenerativeModel("gemini-2.5-flash-preview-04-17")
generation_config = GenerationConfig(
    temperature=0.7,
    max_output_tokens=16384,
)

def summarize_transcript(transcript: str) -> str:
    prompt = f"Please summarize this video. Focus on the main takeaways, summarizing them. Start high level, then go into the details. When participants take specific positions, mention it. As always, keep an eye out for anything unusual or out of the especially notable.\n\n{transcript}\n"

    model_response = gemini_model.generate_content(prompt, generation_config=generation_config)

    return model_response.text
