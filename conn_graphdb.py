from langchain_community.graphs import Neo4jGraph

# Set your Neo4j credentials
NEO4J_URI = "neo4j+s://ee0e839b.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "k30j0sXgLAeCPIkO5Rm4B8CpITcTuuccKejA0nrlBQs"
NEO4J_DATABASE = "neo4j"

# Create the Neo4jGraph connection
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE
)

# Example: Run a simple Cypher query
result = graph.query("MATCH (n) RETURN n LIMIT 5")
print(result)