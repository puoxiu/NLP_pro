from openai import OpenAI
import os


def call_llm(messages: list):
    client = OpenAI(
        base_url= os.getenv("BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )
    
    print(f"base_url = {os.getenv('BASE_URL')}")
    print(f"api_key = {os.getenv('DASHSCOPE_API_KEY')}")
    
    res = client.chat.completions.create(
        model = os.getenv("MODEL_NAME"),
        messages = messages,
        temperature=0.7
    )
    return res.choices[0].message.content