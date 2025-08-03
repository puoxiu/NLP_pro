from pocketflow import Node
import yaml
from utils.mysql_conn import get_db_connection
from utils.call_llm import call_llm

class GetSchema(Node):
    def prep(self, shared):
        return shared['db_name']
    
    def exec(self, prep_res):
        db_name = prep_res
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
        """, (db_name,))
        tables = cursor.fetchall()
        schema = []

        print("=" * 50)

        for table in tables:
            table_name = table['TABLE_NAME']
            schema.append(f"Table: {table_name}")
            
            cursor.execute("""
                SELECT column_name, data_type, column_comment
                FROM information_schema.columns 
                WHERE table_schema = %s 
                AND table_name = %s
                ORDER BY ordinal_position
            """, (db_name, table_name))
            columns = cursor.fetchall()
            for col in columns:
                # 格式：字段名 (数据类型) 注释
                col_desc = f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})"
                if col['COLUMN_COMMENT']:
                    col_desc += f"  # {col['COLUMN_COMMENT']}"
                schema.append(col_desc)
            schema.append("")  # 表之间空一行

        return "\n".join(schema).strip()


    def post(self, shared, prep_res, exec_res):
        shared["schema"] = exec_res
        print("\n===== DB SCHEMA =====\n")
        print(exec_res)
        print("\n=====================\n")



class GenerateSQL(Node):
    def prep(self, shared):
        return shared["natural_query"], shared["schema"]

    def exec(self, prep_res):
        natural_query, schema = prep_res
        prompt = f"""
        Given SQLite schema:
        {schema}

        Question: "{natural_query}"

        Respond ONLY with a YAML block containing the SQL query under the key 'sql':
        ```yaml
        sql: |
        SELECT ...
        ```"""
        llm_response = call_llm(prompt)
        yaml_str = llm_response.split("```yaml")[1].split("```")[0].strip()
        structured_result = yaml.safe_load(yaml_str)
        sql_query = structured_result["sql"].strip().rstrip(';')
        return sql_query

    def post(self, shared, prep_res, exec_res):
        # exec_res is now the parsed SQL query string
        shared["generated_sql"] = exec_res
        # Reset debug attempts when *successfully* generating new SQL
        shared["debug_attempts"] = 0
        print(f"\n===== GENERATED SQL (Attempt {shared.get('debug_attempts', 0) + 1}) =====\n")
        print(exec_res)
        print("\n====================================\n")
        # return "default"

class ExecSQL(Node):
    def prep(self, shared):
        return shared["generated_sql"]

    def exec(self, prep_res):
        sql_query = prep_res
        try:
            is_select = sql_query.strip().upper().startswith("SELECT")
            if not is_select:
                raise ValueError("Only SELECT queries are supported.")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql_query)
            exec_res = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            conn.close()
            return (True, exec_res, column_names)
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return (False, str(e), [])

    def post(self, shared, prep_res, exec_res):
        success, result, column_names = exec_res
        if success:
            shared['final_result'] = result
            shared['column_names'] = column_names
            print("\n===== EXECUTION RESULT =====\n")
            if column_names:
                print("Columns:", ", ".join(column_names))
            for row in result:
                print(row)
            print("\n============================\n")
            return 'success'
        else:
            shared['execution_error'] = result
            shared['debug_attempts'] = shared.get('debug_attempts', 0) + 1
            max_attempts = shared.get('max_attempts', 3)

            print(f"\n===== SQL EXECUTION FAILED (Attempt {shared['debug_attempts']}) =====\n")
            print(f"Error: {shared['execution_error']}")
            print("=========================================\n")

            if shared['debug_attempts'] >= max_attempts:
                print("\n===== MAX DEBUG ATTEMPTS REACHED =====\n")
                print("Please check the SQL query and schema for errors.\n")
                return 
            else:
                print("Attempting to debug the SQL...")
                return "error_retry" # Signal to go to DebugSQL

class DebugSQL(Node):
    def prep(self, shared):
        return (
            shared.get("natural_query"),
            shared.get("schema"),
            shared.get("generated_sql"),
            shared.get("execution_error")
        )

    def exec(self, prep_res):
        natural_query, schema, failed_sql, error_message = prep_res
        prompt = f"""
        The following SQLite SQL query failed:
        ```sql
        {failed_sql}
        ```
        It was generated for: "{natural_query}"
        Schema:
        {schema}
        Error: "{error_message}"

        Provide a corrected SQLite query.

        Respond ONLY with a YAML block containing the corrected SQL under the key 'sql':
        ```yaml
        sql: |
        SELECT ... -- corrected query
        ```"""
        llm_response = call_llm(prompt)

        yaml_str = llm_response.split("```yaml")[1].split("```")[0].strip()
        structured_result = yaml.safe_load(yaml_str)
        corrected_sql = structured_result["sql"].strip().rstrip(';')
        return corrected_sql

    def post(self, shared, prep_res, exec_res):
        # exec_res is the corrected SQL string
        shared["generated_sql"] = exec_res # Overwrite with the new attempt
        shared.pop("execution_error", None) # Clear the previous error for the next ExecuteSQL attempt

        print(f"\n===== REVISED SQL (Attempt {shared.get('debug_attempts', 0) + 1}) =====\n")
        print(exec_res)
        print("\n====================================\n")


class FinalResult(Node):
    def prep(self, shared):
        return shared.get('final_result')

    def exec(self, prep_res):
        return prep_res

    def post(self, shared, prep_res, exec_res):
        shared['final_result'] = exec_res
        print("\n===== FINAL RESULT =====\n")
        print(exec_res)
        print("\n=======================\n")