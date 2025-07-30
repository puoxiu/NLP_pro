from openai import OpenAI
import os
import numpy as np
import requests


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


def fixed_size_chunk(text, chunk_size=2000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks


# def get_embedding(text):
#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
#     response = client.embeddings.create(
#         model="text-embedding-ada-002",
#         input=text
#     )

#     # Extract the embedding vector from the response
#     embedding = response.data[0].embedding
    
#     # Convert to numpy array for consistency with other embedding functions
#     return np.array(embedding, dtype=np.float32)

def get_embedding(text: str):
    if not isinstance(text, str):
        raise ValueError("输入必须是单条字符串文本")
    
    payload = {
        "input": [text],
        "model": "bge-m3-vllm"
    }
    response = requests.post(
        url="http://183.237.186.195:1115/v1/embeddings",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 200:
        # 提取嵌入向量 单条文本对应响应中 data 数组的第一个元素
        data = response.json()
        embedding = np.array(data["data"][0]["embedding"], dtype=np.float32)
        return embedding
    else:
        raise Exception(f"API 请求失败: {response.status_code}, {response.text}")



# if __name__ == "__main__":
    # from dotenv import load_dotenv
    # load_dotenv()
#     emb = get_embedding("你好啊")
#     print(len(emb))
#     print(emb)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("## Testing call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = call_llm(prompt)
    print(f"## Response: {response}")