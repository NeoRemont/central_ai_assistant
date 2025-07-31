import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_gpt_response(prompt, model):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Ошибка GPT: {str(e)}"