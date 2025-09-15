from conn_graphdb import get_neo4j_graph

def delete_all_nodes_and_relationships():
    """Delete all nodes and relationships in the Neo4j database."""
    graph = get_neo4j_graph()
    if not graph:
        raise RuntimeError("Could not connect to Neo4j. Check your credentials and connection.")
    graph.query("MATCH (n) DETACH DELETE n")
    print("All nodes and relationships deleted from Neo4j.")

if __name__ == "__main__":
    delete_all_nodes_and_relationships()
