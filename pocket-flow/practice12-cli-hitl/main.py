from flow import create_flow

from dotenv import load_dotenv

load_dotenv()

def main():
    joke_flow = create_flow()

    shared = {
        'topic': None,
        "current_joke": None,
        'disliked_jokes': [],
        "user_feedback": None
    }
    
    print("开始啦！")
    joke_flow.run(shared=shared)


if __name__ == '__main__':
    main()