import os
import numpy as np
from openai import OpenAI
import requests

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


if __name__ == "__main__":
    # Test the embedding function
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "Python is a popular programming language for data science."
    
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    
    print(f"Embedding 1 shape: {emb1.shape}")
    print(f"Embedding 2 shape: {emb2.shape}")
    
    # Calculate similarity (dot product)
    similarity = np.dot(emb1, emb2)
    print(f"Similarity between texts: {similarity:.4f}") 