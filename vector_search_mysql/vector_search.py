import os
import numpy as np
import psycopg2
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 获取向量
def get_embedding(text: str):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("BASE_URL")
    )

    completion = client.embeddings.create(
        model=os.getenv("MODEL"),
        input=text,
        dimensions=1024,
        encoding_format="float"
    )

    return completion.data[0].embedding


# 建立数据库连接
def get_connection():
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        dbname=os.getenv("PG_DATABASE")
    )


# 插入文档
def insert_document(content: str, file_id: str, user_id: str = None) -> bool:
    try:
        embedding = get_embedding(content)
        # 转为 pgvector 字符串格式
        embedding_str = f"[{', '.join(f'{float(x):.5f}' for x in embedding)}]"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vector_test (file_id, content, embedding)
            VALUES (%s, %s, %s::vector)
        """, (file_id, content, embedding_str))
        conn.commit()
        cur.close()
        conn.close()
        print("✅ 插入成功")
        return True
    except Exception as e:
        print("❌ 插入失败:", e)
        return False



# 搜索相似文档
def search_by_file_id_and_query(
    query: str,
    file_id: str,
    top_k: int = 1
) -> List[Tuple[str, float, Dict]]:
    try:
        embedding = get_embedding(query)
        # 把 Python list 转为 PostgreSQL 向量格式字符串
        embedding_str = f"[{', '.join(f'{float(x):.5f}' for x in embedding)}]"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT content, embedding <#> %s AS distance
            FROM vector_test
            WHERE file_id = %s
            ORDER BY distance ASC
            LIMIT %s
        """, (embedding_str, file_id, top_k))

        results = cur.fetchall()
        cur.close()
        conn.close()

        return [(content, 1 - distance, {}) for content, distance in results]  # 余弦相似度 = 1 - 距离
    except Exception as e:
        print("❌ 查询失败:", e)
        return []


# if __name__ == "__main__":
#     print("== 文档向量测试 ==")
#     mode = input("选择模式：插入文档(i) 或 搜索文档(s)? ")

#     if mode == 'i':
#         file_id = input("输入 file_id：")
#         content = input("输入内容：")
#         insert_document(content, file_id)
#     elif mode == 's':
#         file_id = input("输入 file_id：")
#         query = input("输入搜索内容：")
#         results = search_by_file_id_and_query(query, file_id)
#         print("== 检索结果 ==")
#         for i, (content, score, _) in enumerate(results, 1):
#             print(f"[{i}] 相似度: {score:.4f}, 内容: {content}")
#     else:
#         print("无效输入，请输入 'i' 或 's'")


if __name__ == "__main__":
    print("== 自动测试向量插入与检索 ==")
    
    file_id = "test_file_001"
    docs = [
        "人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的系统。",
        "天气不错，适合出去散步。",
        "深度学习是机器学习的一种方法，特别适合处理图像和自然语言。"
    ]
    
    print("🚀 开始插入测试文档")
    for doc in docs:
        insert_document(doc, file_id)

    print("\n🔍 执行检索：")
    query = "人工智能和深度学习的区别是什么？"
    results = search_by_file_id_and_query(query, file_id, top_k=3)
    
    print("== 检索结果 ==")
    for i, (content, score, _) in enumerate(results, 1):
        print(f"[{i}] 相似度: {score:.4f}\n内容: {content}\n")


