from flow import create_text_2_sql_flow

from dotenv import load_dotenv

def main():
    text_2_sql_flow = create_text_2_sql_flow()

    natural_query = input("请输入：")

    shared = {
        'db_name':'xingoa',
        'natural_query': natural_query
    }

    text_2_sql_flow.run(shared)

load_dotenv()
if __name__ == '__main__':
    main()