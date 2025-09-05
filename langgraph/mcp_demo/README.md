

## 运行流程

```bash
# 1) 启动 HTTP 天气 MCP 服务
python weather_server.py

# 2) 运行代理（会自动通过 stdio 启动 math_server.py）
python agent_with_mcp.py

```

## 输出示例
```bash
(langgraph) xing@xing-2 mcp_demo % python agent_with_mcp.py
math_mcp path: /Users/xing/Desktop/test/go-ai/pocket-flow/NLP_pro/langgraph/mcp_demo/math_server.py
Processing request of type ListToolsRequest
Processing request of type CallToolRequest
Processing request of type ListToolsRequest
Processing request of type CallToolRequest
Processing request of type ListToolsRequest

[Math Response]
 (3 + 5) * 12 = 96

[Weather Response]
 The weather in NYC is always sunny! 🌞

[Local Tool Response]
 MCP 是一种用于将外部工具或资源通过统一协议暴露给 LLM（大语言模型）的协议。
```