
# 模型选择与环境

GPU：AutoDL, vGPU-32GB
model：Qwen3-8B
url：魔塔社区下载

## 安装 & 源码
```bash
# 最新版本transformers
pip install transformers

git clone https://github.com/QwenLM/Qwen3.git
```

## 测试代码

```python
from modelscope import AutoModelForCausalLM, AutoTokenizer

model_name = "/root/autodl-tmp/Qwen/Qwen3-8B"

# load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

# prepare the model input
prompt = "你是谁呀？"
messages = [
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# conduct text completion
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=32768
)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

# parsing thinking content
try:
    # rindex finding 151668 (</think>)
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

print("thinking content:", thinking_content)
print("content:", content)
```

# vLLM部署-单卡

```bash
pip install vllm


python3 -m vllm.entrypoints.openai.api_server \
  --model /root/autodl-tmp/Qwen/Qwen3-8B \
  --trust-remote-code


curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/root/autodl-tmp/Qwen/Qwen3-8B",
    "messages": [
      {"role": "user", "content": "帮我生成一首诗歌吧，以实习为题"}
    ],
    "max_tokens": 512,
    "temperature": 0.7,
    "stream": false
  }'
```

# SGLang 部署

```bash
pip install vllm
pip install sglang orjson torchao
pip install sgl_kernel

# 非思考模式
python -m sglang.launch_server --model-path /root/autodl-tmp/Qwen/Qwen3-8B --port 8000 --reasoning-parser qwen3
# 思考模式
python -m sglang.launch_server --model-path /root/autodl-tmp/Qwen/Qwen3-8B --port 8000

