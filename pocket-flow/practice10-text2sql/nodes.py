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

