from openai import OpenAI
import os

def call_llm(prompt):
    client = OpenAI(
        base_url= os.getenv("BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )
    res = client.chat.completions.create(
        model = os.getenv("MODEL_NAME"),
        messages = [{
            "role": "user",
            "content": prompt
        }]
    )
    return res.choices[0].message.content