# weather_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    # 这里演示写死数据；真实场景可接第三方天气 API
    return f"It's always sunny in {location}"

if __name__ == "__main__":
    # 启动一个 HTTP(流式) MCP 端点，默认 0.0.0.0:8000
    mcp.run(transport="streamable-http")
