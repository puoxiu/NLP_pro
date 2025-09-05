from langchain_core.tools import tool


# ===== 2.1 定义一个“本地 Tool”（非 MCP） =====
@tool
def search_docs(keyword: str) -> str:
    """在项目内微型知识库里检索。演示用，实际可接数据库/向量检索。"""
    corpus = {
        "LangGraph": "LangGraph 是一个用图来组织代理/工作流的编排框架。",
        "MCP": "MCP 是一种用于把外部工具/资源通过统一协议暴露给 LLM 的协议。"
    }
    for k, v in corpus.items():
        if keyword.lower() in k.lower() or keyword.lower() in v.lower():
            return f"命中: {k} -> {v}"
    return "未命中"