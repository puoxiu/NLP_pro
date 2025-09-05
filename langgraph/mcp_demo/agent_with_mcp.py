import asyncio
import sys
from pathlib import Path
from typing import List

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import MessagesState
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tools import search_docs

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)

# ===== 连接多个 MCP 服务器 =====

# math mcp 是stdio传输方式，需本地拉起调用
THIS_DIR = Path(__file__).parent.resolve()
MATH_PATH = str(THIS_DIR / "math_server.py")

print(f"math_mcp path: {MATH_PATH}")

client = MultiServerMCPClient(
    {
        "math": {
            "command": sys.executable,          # 用当前 Python 解释器
            "args": [MATH_PATH],
            "transport": "stdio",
        },
        "weather": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        },
    }
)


# =====  LangGraph：把 MCP 工具 + 本地工具绑定到模型 & ToolNode =====

async def build_agent():
    mcp_tools = await client.get_tools()   # 从 MCP 服务器拉取工具描述
    tools = mcp_tools + [search_docs]     # 合并本地工具
    model_with_tools = model.bind_tools(tools)
    tool_node = ToolNode(tools)

    def should_continue(state: MessagesState) -> str:
        """根据消息状态判断是否继续执行"""
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "tools"
        return "end"
    
    async def call_model(state: MessagesState):
        resp = await model_with_tools.ainvoke(state["messages"])
        return {"messages": [resp]}
    
    # 构建图
    graph = StateGraph(MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "call_model")
    graph.add_conditional_edges("call_model", should_continue, {
        "tools": "tools",
        "end": END,
    })
    graph.add_edge("tools", "call_model")

    return graph.compile()

# ===== 2.5 运行并测试 =====
async def main():
    graph = await build_agent()

    # A. 触发 MCP: math.add / math.multiply
    r1 = await graph.ainvoke({"messages": [HumanMessage(content="What's (3 + 5) * 12?") ]})
    print("\n[Math Response]\n", r1["messages"][-1].content)

    # B. 触发 MCP: weather.get_weather
    r2 = await graph.ainvoke({"messages": [HumanMessage(content="What's the weather in NYC?")]})
    print("\n[Weather Response]\n", r2["messages"][-1].content)

    # C. 触发本地 Tool: search_docs
    r3 = await graph.ainvoke({"messages": [HumanMessage(content="在文档里找一下 MCP 是什么")]})
    print("\n[Local Tool Response]\n", r3["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())