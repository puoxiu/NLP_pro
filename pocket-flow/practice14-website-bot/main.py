import sys

from flow import create_flow
from logger import ColoredLogger

def init():
    if len(sys.argv) < 2:
        ColoredLogger.error("Usage: python main.py <start_url1> [start_url2] ... ' [instruction]")
        ColoredLogger.info("Example: python main.py https://example.com ")
        sys.exit(1)

    start_urls = sys.argv[1:]
    instruction = "Provide helpful and accurate answers based on the website content."

    for url in start_urls:
        if not url.startswith(('http://', 'https://')):
            ColoredLogger.error(f"Error: '{url}' is not a valid URL. URLs must start with http:// or https://")
            sys.exit(1)


    shared = {
        'instruction': instruction,
        "allowed_domains": list(set(start_urls)),   ## 允许的域名前缀，默认是初始输入url
        "all_discovered_urls": start_urls.copy(),
        "visited_urls": set(),
        "url_graph": {},
        "url_content": {},

        # Per-run state (will be set in the loop)
        "user_question": "",
        "urls_to_process": [],
        "final_answer": None
    }

    return start_urls, shared


def main():
    start_urls, shared = init()

    flow = create_flow()

    is_first_run = True
    while True:
        if is_first_run:
            shared["urls_to_process"] = list(range(len(start_urls)))
            is_first_run = False
        else:
            shared["urls_to_process"] = []
        
        question = input("\n请输入您的问题(按Ctrl+C or 输入exit退出): ")
        if question == 'exit':
            ColoredLogger.info("拜拜啦！")
            break

        if not question.strip():
            continue
        shared['user_question'] = question

        ColoredLogger.info(f"\n===正在回答：{question} ===")

        flow.run(shared=shared)


if __name__ == '__main__':
    main()
