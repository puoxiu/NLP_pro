# To install: pip install tavily-python
from tavily import TavilyClient
client = TavilyClient("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")
response = client.search(
    query="广州天气"
)
print(response)