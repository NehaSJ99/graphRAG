from conn_databricks import execute_sql
from conn_graphdb import get_neo4j_graph
import json

def get_table_columns():
    """Return a dict of table_name -> list of column names from Databricks."""
    tables = execute_sql("SHOW TABLES")
    table_columns = {}
    for table in tables:
        table_name = table[1]
        columns = execute_sql(f"DESCRIBE TABLE {table_name}")
        table_columns[table_name] = [col[0] for col in columns]
    return table_columns

def create_table_and_column_nodes(graph, table_columns):
    """Create Table and Column nodes and HAS_COLUMN relationships in Neo4j."""
    for table_name, columns in table_columns.items():
        graph.query(
            "MERGE (t:Table {name: $table_name})",
            params={"table_name": table_name}
        )
        for col_name in columns:
            graph.query(
                '''
                MERGE (c:Column {name: $col_name, table: $table_name})
                MERGE (t:Table {name: $table_name})
                MERGE (t)-[:HAS_COLUMN]->(c)
                ''',
                params={"col_name": col_name, "table_name": table_name}
            )

def infer_foreign_keys(table_columns):
    """Infer foreign key relationships as a list of (fk_table, fk_column, pk_table, pk_column)."""
    fk_relationships = []
    for table_name, columns in table_columns.items():
        for col_name in columns:
            if col_name.endswith('_id'):
                for ref_table, ref_columns in table_columns.items():
                    pk_candidates = [c for c in ref_columns if c.endswith('_id')]
                    if col_name in pk_candidates and ref_table != table_name:
                        fk_relationships.append((table_name, col_name, ref_table, col_name))
    return fk_relationships

def create_foreign_key_relationships(graph, fk_relationships):
    """Create FOREIGN_KEY relationships in Neo4j from a list of (fk_table, fk_column, pk_table, pk_column)."""
    for fk_table, fk_column, pk_table, pk_column in fk_relationships:
        graph.query(
            '''
            MATCH (src:Table {name: $fk_table}), (dst:Table {name: $pk_table})
            MERGE (src)-[r:FOREIGN_KEY {fk_column: $fk_column, pk_column: $pk_column}]->(dst)
            ''',
            params={
                "fk_table": fk_table,
                "pk_table": pk_table,
                "fk_column": fk_column,
                "pk_column": pk_column
            }
        )

def get_primary_keys(table_name):
    """Infer primary keys for a table (simple heuristic: columns ending with '_id' and matching table name)."""
    columns = execute_sql(f"DESCRIBE TABLE {table_name}")
    pk_candidates = [col[0] for col in columns if col[0].endswith('_id')]
    # Heuristic: if table is 'orders', look for 'order_id' as PK
    likely_pk = [c for c in pk_candidates if c.startswith(table_name.rstrip('s')+'_id')]
    return likely_pk or pk_candidates

def build_schema_json(table_columns, fk_relationships):
    schema = []
    for table_name, columns in table_columns.items():
        primary_keys = get_primary_keys(table_name)
        foreign_keys = []
        for fk_table, fk_column, pk_table, pk_column in fk_relationships:
            if fk_table == table_name:
                foreign_keys.append({
                    "column": fk_column,
                    "references": {"table": pk_table, "column": pk_column}
                })
        schema.append({
            "table": table_name,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys
        })
    return schema

def main():
    graph = get_neo4j_graph()
    if not graph:
        raise RuntimeError("Could not connect to Neo4j. Check your credentials and connection.")
    table_columns = get_table_columns()
    fk_relationships = infer_foreign_keys(table_columns)
    schema_json = build_schema_json(table_columns, fk_relationships)
    print(json.dumps(schema_json, indent=2))
    # Optionally: create_table_and_column_nodes(graph, table_columns)
    # Optionally: create_foreign_key_relationships(graph, fk_relationships)
    # print("Schema and relationships created in Neo4j.")

if __name__ == "__main__":
    main()