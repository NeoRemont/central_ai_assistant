import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt):
    response = await openai.ChatCompletion.acreate(
        model=os.getenv("GPT_MODEL", "gpt-4-turbo"),
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
