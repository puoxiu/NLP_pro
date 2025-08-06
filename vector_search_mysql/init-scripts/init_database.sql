USE vector_db;

CREATE TABLE IF NOT EXISTS document_embeddings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1024) NOT NULL,  -- 向量维度
    metadata JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_id ON document_embeddings((metadata->>'$.file_id'));

-- 创建向量索引（加速相似性搜索）
CREATE INDEX IF NOT EXISTS idx_embedding ON document_embeddings(embedding)
USING HNSW WITH (distance_function = 'COSINE');

GRANT ALL PRIVILEGES ON vector_db.* TO 'vector_user'@'%';
FLUSH PRIVILEGES;