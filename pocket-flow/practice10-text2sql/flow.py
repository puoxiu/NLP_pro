from pocketflow import Flow

from nodes import GetSchema, GenerateSQL



def create_text_2_sql_flow():
    get_schema_node = GetSchema()
    generate_sql_node = GenerateSQL()

    get_schema_node >> generate_sql_node

    text_2_sql_flow = Flow(start=get_schema_node)

    return text_2_sql_flow