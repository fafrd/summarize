import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

vertexai.init(project='elegant-gearing-417520', location='us-central1')

gemini_model = GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
generation_config = GenerationConfig(
    temperature=0.7,
    max_output_tokens=8192,
)

def summarize_transcript(transcript):
    """Generates a summary of the transcript using an LLM."""

    prompt = f"Please summarize this Youtube video. Focus on the main takeaways, summarizing them. When participants take specific positions, mention it. Look for anything controversial or out of the ordinary.\n\n{transcript}\n"

    model_response = gemini_model.generate_content(prompt, generation_config=generation_config)

    return model_response.text
