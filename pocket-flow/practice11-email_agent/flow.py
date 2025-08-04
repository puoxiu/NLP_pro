from pocketflow import Flow

from nodes import Router

def create_flow():
    router_node = Router()

    flow = Flow(start=router_node)

    return flow