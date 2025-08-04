from pocketflow import Node

from utils.call_llm import call_llm

class GetTopicNode(Node):
    def exec(self, _shared):
        inputs = input("您喜欢关于什么topic的joke? (输入‘exit’退出)\n")

        return inputs
    

    def post(self, shared, _prep_res, exec_res):
        topic = exec_res
        if topic in ('exit', 'EXIT'):
            return 'exit'
    
        shared["topic"] = exec_res
        return

class ExitNode(Node):
    # def prep(self, shared):
    #     return super().prep(shared)
    
    # def exec(self, prep_res):
    #     return super().exec(prep_res)
    
    # def post(self, shared, prep_res, exec_res):
    #     return super().post(shared, prep_res, exec_res)
    pass

class GenerateJokeNode(Node):
    """根据topic和历史反馈生成joke"""
    def prep(self, shared):
        topic = shared.get("topic", "anything")
        disliked_jokes = shared.get("disliked_jokes", [])
        
        prompt = f"请围绕{topic}这个主题，创作一个简短而有趣的单句笑话。"
        if disliked_jokes:
            disliked_str = "; ".join(disliked_jokes)
            prompt = f"用户不喜欢以下笑话：[{disliked_str}]。请生成一个关于{topic}的新的、不同的笑话。"

        return prompt

    def exec(self, prep_res):
        return call_llm(prep_res)

    def post(self, shared, _prep_res, exec_res):
        shared["current_joke"] = exec_res
        print(f"\nJoke: {exec_res}")



class GetFeedbackNode(Node):
    """Presents the joke to the user and asks for approval."""
    def exec(self, _prep_res):
        while True:
            feedback = input("Did you like this joke? (yes/no): ").strip().lower()
            if feedback in ["yes", "y", "no", "n"]:
                return feedback
            print("Invalid input. Please type 'yes' or 'no'.")

    def post(self, shared, _prep_res, exec_res):
        if exec_res in ["yes", "y"]:
            shared["user_feedback"] = "approve"
            print("Great! Glad you liked it.")
            return "Approve"
        else:
            shared["user_feedback"] = "disapprove"
            current_joke = shared.get("current_joke")
            if current_joke:
                if "disliked_jokes" not in shared:
                    shared["disliked_jokes"] = []
                shared["disliked_jokes"].append(current_joke)
            print("Okay, let me try another one.")
            return "Disapprove" 