from conn_graphdb import get_neo4j_graph
from embed_schema import main as get_embeddings

def print_nodes_and_relationships():
    """Print the node and relationship descriptions that would be embedded and created."""
    # Get the same descriptions as would be embedded
    table_columns = None
    fk_relationships = None
    llm_output = None
    # Call embed_schema.main() but intercept the process to get descriptions and LLM output
    import embed_schema
    table_columns = embed_schema.get_tables_and_columns()
    fk_relationships = embed_schema.infer_foreign_keys(table_columns)
    llm_output = embed_schema.get_relationships_from_llm(
        tables=list(table_columns.keys()),
        columns=table_columns,
        fk_relationships=fk_relationships
    )
    #print("Tables and columns:", table_columns)
    #print("Foreign key relationships:", fk_relationships)
    #print("\nLLM-Inferred Nodes and Relationships:\n", llm_output)
    # Prepare descriptions for embedding (tables, columns, relationships)
    descriptions = []
    for table, columns in table_columns.items():
        descriptions.append(f"Table: {table} | Columns: {', '.join(columns)}")
    for fk in fk_relationships:
        descriptions.append(f"{fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]} (FK)")
    # Add LLM-inferred output as well
    if llm_output:
        for line in llm_output.split('\n'):
            if line.strip():
                descriptions.append(line.strip())
    print("\nAll node and relationship descriptions to be embedded:")
    for desc in descriptions:
        print(desc)

if __name__ == "__main__":
    print_nodes_and_relationships()