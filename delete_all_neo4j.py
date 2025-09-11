from conn_graphdb import graph

def delete_all_nodes_and_relationships():
    """Delete all nodes and relationships in the Neo4j database."""
    graph.query("MATCH (n) DETACH DELETE n")
    print("All nodes and relationships deleted from Neo4j.")

if __name__ == "__main__":
    delete_all_nodes_and_relationships()
