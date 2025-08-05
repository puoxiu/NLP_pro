from pocketflow import Flow

from nodes import CrawlAndExtract

def create_flow():
    crawl_and_extract_node = CrawlAndExtract()


    flow = Flow(start=crawl_and_extract_node)

    return flow