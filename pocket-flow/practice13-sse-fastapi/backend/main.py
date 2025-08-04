from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import asyncio
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", 'null'],  # Vue前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求体模型
class ChatRequest(BaseModel):
    prompt: str

async def llm_stream(prompt: str):
    """流式获取LLM响应"""
    try:
        # 在函数内部初始化OpenAI客户端，而不是全局初始化
        client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("DASHSCOPE_API_KEY")
        )
        
        # 调用LLM的流式接口
        stream = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[{"role": "user", "content": prompt}],
            stream=True,  # 启用流式响应
        )
        
        # 逐个返回流式数据
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                # 以SSE格式返回数据
                yield f"data: {content}\n\n"
                # 短暂休眠，避免数据推送过快
                await asyncio.sleep(0.01)
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: 发生错误: {str(e)}\n\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    """处理聊天请求，返回SSE响应"""
    return StreamingResponse(
        llm_stream(request.prompt),
        media_type="text/event-stream"
    )

# 根路由，用于测试
@app.get("/")
async def root():
    return {"message": "LLM SSE 服务已启动"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
