from openai import OpenAI
import os
from dotenv import load_dotenv
import time
from pocketflow import AsyncFlow, AsyncParallelBatchNode

load_dotenv()


async def call_llm(prompt):
    client = OpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )
    
    # 使用 asyncio.to_thread 将同步调用包装为异步
    def sync_call():
        return client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
    
    # 在单独的线程中执行同步调用，不阻塞事件循环
    res = await asyncio.to_thread(sync_call)
    return res.choices[0].message.content


class TranslateTextNodeParallel(AsyncParallelBatchNode):
    """Translates README into multiple languages in parallel and saves files."""
    async def prep_async(self, shared):
        """Reads text and target languages from shared store."""
        text = shared.get("text", "(No text provided)")
        languages = shared.get("languages", [])
        return [(text, lang) for lang in languages]

    async def exec_async(self, data_tuple):
        """Calls the async LLM utility for each target language."""
        text, language = data_tuple
        
        prompt = f"""
        Please translate the following markdown file into {language}. 
        But keep the original markdown format, links and code blocks.
        Directly return the translated text, without any other text or comments.

        Original: 
        {text}

        Translated:"""
                
        result = await call_llm(prompt)
        print(f"Translated {language} text")
        return {"language": language, "translation": result}

    async def post_async(self, shared, prep_res, exec_res_list):
        """Stores the dictionary of {language: translation} pairs and writes to files."""
        output_dir = shared.get("output_dir", "data")
        os.makedirs(output_dir, exist_ok=True)
        
        for result in exec_res_list:
            if isinstance(result, dict):
                language = result.get("language", "unknown")
                translation = result.get("translation", "")
                
                filename = os.path.join(output_dir, f"README_{language.upper()}.md")
                try:
                    import aiofiles
                    async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                        await f.write(translation)
                    print(f"Saved translation to {filename}")
                except ImportError:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(translation)
                    print(f"Saved translation to {filename} (sync fallback)")
                except Exception as e:
                    print(f"Error writing file {filename}: {e}")
            else:
                print(f"Warning: Skipping invalid result item: {result}")
        return "default"


def create_parallel_translation_flow():
    """Creates and returns the parallel translation flow."""
    translate_node = TranslateTextNodeParallel(max_retries=3)
    return AsyncFlow(start=translate_node)

import asyncio
async def main():
    source_readme_path = "./README.md"
    try:
        with open(source_readme_path, "r", encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find the source README file at {source_readme_path}")
        exit(1)
    except Exception as e:
        print(f"Error reading file {source_readme_path}: {e}")
        exit(1)

    shared = {
        "text": text,
        "languages": ["Chinese", "Spanish", "Japanese", "German", "Russian", "French", "Korean"],
        "output_dir": "data"
    }

    translation_flow = create_parallel_translation_flow()

    print(f"Starting parallel translation into {len(shared['languages'])} languages...")
    start_time = time.perf_counter()

    await translation_flow.run_async(shared)

    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"\nTotal parallel translation time: {duration:.4f} seconds")
    print("\n=== Translation Complete ===")
    print(f"Translations saved to: {shared['output_dir']}")
    print("============================")

if __name__ == "__main__":
    asyncio.run(main()) 
    # 在jupyter中直接：
    # await main()