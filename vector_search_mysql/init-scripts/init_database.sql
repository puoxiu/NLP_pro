-- 安装 pgvector 插件
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建表结构
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  file_id TEXT NOT NULL,
  content TEXT,
  embedding VECTOR(3)
);

-- 插入示例数据
-- INSERT INTO documents (file_id, content, embedding) VALUES
-- ('file1', '这是第一个文档', '[0.1, 0.2, 0.3]'),
-- ('file1', '这是第二个文档', '[0.2, 0.1, 0.4]'),
-- ('file2', '这是第三个文档', '[0.9, 0.1, 0.1]');

CREATE TABLE vector_test (
  id SERIAL PRIMARY KEY,
  file_id TEXT NOT NULL,
  content TEXT,
  embedding VECTOR(1024)
);