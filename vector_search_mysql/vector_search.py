import requests
import numpy as np
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()


def get_embedding(text: str):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url=os.getenv("BASE_URL")  # 百炼服务的base_url
    )

    completion = client.embeddings.create(
        model=os.getenv("MODEL"),
        # model = "text-embedding-v4",
        input=text,
        dimensions=1024, 
        encoding_format="float"
    )

    # print(completion.model_dump_json())

    return completion.data[0].embedding


# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "database": "vector_db",
    "user": "root",
    "password": "root123456",
    "port": 3306
}



def insert_document(content: str, file_id: str, user_id: str) -> bool:
    """插入文档内容、向量和元数据到数据库"""
    try:
        # 生成向量
        embedding = get_embedding(content)
        
        # 准备元数据
        metadata = {
            "file_id": file_id,
            "user_id": user_id,
            "content_length": len(content)
        }
        
        conn = mysql.connector.connect(** DB_CONFIG)
        cursor = conn.cursor()
        
        # 插入数据
        query = """
        INSERT INTO document_embeddings (content, embedding, metadata)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (content, embedding, str(metadata).replace("'", '"')))
        conn.commit()
        print(f"文档插入成功，file_id: {file_id}")
        return True
        
    except Error as e:
        print(f"数据库错误: {e}")
        return False
    except Exception as e:
        print(f"插入失败: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def search_by_file_id_and_query(
    query: str, 
    file_id: str, 
    top_k: int = 5
) -> List[Tuple[str, float, Dict]]:
    """
    根据file_id过滤文档，并按查询与文档的相似性返回结果
    返回: [(内容, 相似度, 元数据), ...]
    """
    try:
        # 生成查询向量
        query_embedding = get_embedding(query)
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 执行检索：按file_id过滤并按余弦相似度排序
        query_sql = """
        SELECT 
            content,
            VECTOR_COSINE_SIMILARITY(embedding, %s) AS similarity,
            metadata
        FROM document_embeddings
        WHERE metadata->>'$.file_id' = %s
        ORDER BY similarity DESC
        LIMIT %s
        """
        
        cursor.execute(query_sql, (query_embedding.tolist(), file_id, top_k))
        results = cursor.fetchall()
        
        # 处理结果，将metadata从字符串转换为字典
        processed_results = []
        for res in results:
            metadata = eval(res['metadata'])  # 将JSON字符串转换为字典
            processed_results.append((
                res['content'],
                res['similarity'],
                metadata
            ))
        
        return processed_results
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return []
    except Exception as e:
        print(f"检索失败: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()



if __name__ == "__main__":
    text = input("请输入要转为向量的测试文本：")

    embedding = get_embedding(text)
    dimension = len(embedding)
    print(f"嵌入维度为：{dimension}")   # 1024
    
    
    # 插入file_id为"doc_001"的文档
    # insert_document(
    #     content="Python是一种广泛使用的高级编程语言，由Guido van Rossum于1989年圣诞节期间设计",
    #     file_id="doc_001",
    #     user_id="user_123"
    # )
    
    # insert_document(
    #     content="Python的设计哲学强调代码的可读性和简洁性，采用缩进来定义代码块",
    #     file_id="doc_001",
    #     user_id="user_123"
    # )
    
    # # 插入file_id为"doc_002"的文档
    # insert_document(
    #     content="MySQL是一个关系型数据库管理系统，由瑞典MySQL AB公司开发",
    #     file_id="doc_002",
    #     user_id="user_123"
    # )
    
    # # 3. 检索示例：查询与"Python特点"相关的内容，限定file_id为"doc_001"
    # search_results = search_by_file_id_and_query(
    #     query="Python有什么特点？",
    #     file_id="doc_001",
    #     top_k=2
    # )
    
    # # 4. 打印检索结果
    # print("\n检索结果:")
    # for i, (content, similarity, metadata) in enumerate(search_results, 1):
    #     print(f"\n结果 {i} (相似度: {similarity:.4f}):")
    #     print(f"内容: {content}")
    #     print(f"文件ID: {metadata['file_id']}")

