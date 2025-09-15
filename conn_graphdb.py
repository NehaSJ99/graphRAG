from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import os

def load_neo4j_env():
    """Load Neo4j credentials from environment variables."""
    load_dotenv()
    return {
        "url": os.getenv("NEO4J_URI"),
        "username": os.getenv("NEO4J_USERNAME"),
        "password": os.getenv("NEO4J_PASSWORD"),
        "database": os.getenv("NEO4J_DATABASE"),
    }

def get_neo4j_graph():
    """Create and return a Neo4jGraph connection, or print error if connection fails."""
    creds = load_neo4j_env()
    try:
        graph = Neo4jGraph(
            url=creds["url"],
            username=creds["username"],
            password=creds["password"],
            database=creds["database"]
        )
        # Test connection
        graph.query("RETURN 1")
        return graph
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
        return None

# Singleton graph connection for import convenience
graph = get_neo4j_graph()

# # Example: Run a simple Cypher query
# if graph:
#     result = graph.query("MATCH (n) RETURN n LIMIT 5")
#     print(result)