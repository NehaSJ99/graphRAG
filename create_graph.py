from conn import execute_sql
from conn_graphdb import graph

tables = execute_sql("SHOW TABLES")
for table in tables:
    table_name = table[1]  # 2nd column is table name
    columns = execute_sql(f"DESCRIBE TABLE {table_name}")

    # Step 1: Create Table nodes

    from conn import execute_sql
    from conn_graphdb import graph

    # Step 1: Get all tables and columns
    tables = execute_sql("SHOW TABLES")
    table_columns = {}
    for table in tables:
        table_name = table[1]
        columns = execute_sql(f"DESCRIBE TABLE {table_name}")
        table_columns[table_name] = [col[0] for col in columns]
        # Create Table node
        graph.query(
            "MERGE (t:Table {name: $table_name})",
            params={"table_name": table_name}
        )
        # Create Column nodes and HAS_COLUMN relationships
        for col in columns:
            col_name = col[0]
            graph.query(
                '''
                MERGE (c:Column {name: $col_name, table: $table_name})
                MERGE (t:Table {name: $table_name})
                MERGE (t)-[:HAS_COLUMN]->(c)
                '''
                ,
                params={"col_name": col_name, "table_name": table_name}
            )

    # Step 2: Dynamically infer foreign keys
    # For each table, look for columns ending with _id (except its own PK)
    for table_name, columns in table_columns.items():
        for col_name in columns:
            if col_name.endswith('_id'):
                # Try to find another table where this column is the PK
                for ref_table, ref_columns in table_columns.items():
                    # Heuristic: PK is <table>_id or first column ending with _id
                    pk_candidates = [c for c in ref_columns if c.endswith('_id')]
                    if col_name in pk_candidates and ref_table != table_name:
                        # Create FOREIGN_KEY relationship
                        graph.query(
                            '''
                            MATCH (src:Table {name: $fk_table}), (dst:Table {name: $pk_table})
                            MERGE (src)-[r:FOREIGN_KEY {fk_column: $fk_column, pk_column: $pk_column}]->(dst)
                            '''
                            ,
                            params={
                                "fk_table": table_name,
                                "pk_table": ref_table,
                                "fk_column": col_name,
                                "pk_column": col_name
                            }
                        )