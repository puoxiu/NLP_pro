from pocketflow import Flow

from nodes import GetSchema, GenerateSQL, ExecSQL, DebugSQL, FinalResult



def create_text_2_sql_flow():
    get_schema_node = GetSchema()
    generate_sql_node = GenerateSQL()
    exec_sql_node = ExecSQL()
    debug_sql_node = DebugSQL()
    final_result_node = FinalResult()

    get_schema_node >> generate_sql_node >> exec_sql_node
    exec_sql_node - 'error_retry' >> debug_sql_node
    exec_sql_node - 'success' >> final_result_node
    debug_sql_node >> exec_sql_node

    text_2_sql_flow = Flow(start=get_schema_node)

    return text_2_sql_flow