from conn import execute_sql
from conn_graphdb import graph

tables = execute_sql("SHOW TABLES")
for table in tables:
    table_name = table[1]  # 2nd column is table name
    columns = execute_sql(f"DESCRIBE TABLE {table_name}")

for table in tables:
    table_name = table[1]
    graph.query(
        "MERGE (t:Table {name: $table_name})",
        params={"table_name": table_name}
    )
    columns = execute_sql(f"DESCRIBE TABLE {table_name}")
    for col in columns:
        col_name = col[0]
        graph.query(
            '''
            MERGE (c:Column {name: $col_name, table: $table_name})
            MERGE (t:Table {name: $table_name})
            MERGE (t)-[:HAS_COLUMN]->(c)
            ''',
            params={"col_name": col_name, "table_name": table_name}
        )