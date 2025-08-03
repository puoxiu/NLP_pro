import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

# 配置连接池
POOL = PooledDB(
    creator=pymysql,        # 使用的数据库驱动
    maxconnections=10,      # 连接池最大连接数
    mincached=2,            # 初始化时连接池中的最小空闲连接
    maxcached=5,            # 连接池中的最大空闲连接
    maxshared=0,            # 共享连接的最大数量（一般设为0）
    blocking=True,          # 当连接池无可用连接时，是否阻塞等待
    maxusage=None,          # 单个连接的最大使用次数（None表示无限制）
    setsession=[],          # 连接建立后执行的SQL命令列表
    ping=1,                 # 每隔多久检查连接有效性（1表示每次使用前检查）
    host="127.0.0.1",
    user="root",
    password="root123456",
    database="xingoa",
    port=3306,
    charset="utf8mb4",
    cursorclass=DictCursor
)

# 1. 获取数据库连接（从连接池获取，而非新建）
def get_db_connection():
    """从连接池获取数据库连接"""
    return POOL.connection() 




# 2. 获取所有表信息
def get_all_table_info():
    conn = None
    try:
        conn = get_db_connection()
        db_name = "xingoa"
        
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                table_name AS 表名,
                engine AS 存储引擎,
                table_rows AS 记录数,
                create_time AS 创建时间,
                update_time AS 最后更新时间,
                table_comment AS 表注释
            FROM 
                information_schema.tables 
            WHERE 
                table_schema = %s
            ORDER BY 
                table_name ASC
            """
            cursor.execute(sql, (db_name,))
            return cursor.fetchall()
            
    except Exception as e:
        print(f"获取表信息失败: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()  # 这里的close()是将连接放回连接池，而非真正关闭

if __name__ == "__main__":
    db_conn = get_db_connection()
    print("数据库连接成功（来自连接池）")
    
    tables = get_all_table_info()
    if tables:
        print(f"\n数据库 'xingoa' 中的表信息如下：")
        print(f"{'表名':<20} {'存储引擎':<10} {'记录数':<10} {'表注释'}")
        print("-" * 70)
        for table in tables:
            print(
                f"{table['表名']:<20} "
                f"{table['存储引擎']:<10} "
                f"{str(table['记录数']):<10} "
                f"{table['表注释']}"
            )
    else:
        print("\n未查询到表信息")
    