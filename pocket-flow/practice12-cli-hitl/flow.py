from pocketflow import Flow

from nodes import GetTopicNode, GenerateJokeNode, GetFeedbackNode, ExitNode

def create_flow():
    get_topic_node = GetTopicNode()
    generate_joke_node = GenerateJokeNode()
    get_feedback_node = GetFeedbackNode()
    exit_node = ExitNode()

    get_topic_node >> generate_joke_node
    get_topic_node - 'exit' >> exit_node
    generate_joke_node >> get_feedback_node
    get_feedback_node - 'Disapprove' >> generate_joke_node
    get_feedback_node - 'Approve' >> get_topic_node

    flow = Flow(start=get_topic_node)

    return flow


