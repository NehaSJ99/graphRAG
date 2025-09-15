import os
import openai
from dotenv import load_dotenv
from create_graph import get_table_columns, infer_foreign_keys

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

def get_tables_and_columns():
    """Get tables and their columns from Databricks."""
    return get_table_columns()

def get_fk_relationships():
    """Get inferred foreign key relationships as a list."""
    table_columns = get_tables_and_columns()
    return infer_foreign_keys(table_columns)

def get_relationships_from_llm(tables, columns, fk_relationships):
    """Send tables, columns, and FKs to OpenAI LLM to get meaningful relationships and nodes."""
    prompt = (
        "Given the following database tables, columns, and foreign key relationships, "
        "identify and describe the most meaningful nodes and relationships for a knowledge graph.\n\n"
        f"Tables and columns: {tables}\n\nForeign keys: {fk_relationships}\n\n"
        "List the nodes and relationships as: Node(type, name), Relationship(source, target, type, description)"
    )
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def create_embeddings_from_descriptions(descriptions):
    """Create OpenAI embeddings from a list of descriptions."""
    client = openai.OpenAI()
    response = client.embeddings.create(input=descriptions, model=EMBEDDING_MODEL)
    return [d.embedding for d in response.data]

def main():
    table_columns = get_tables_and_columns()
    fk_relationships = infer_foreign_keys(table_columns)
    print("Tables and columns:", table_columns)
    print("Foreign key relationships:", fk_relationships)
    # Get LLM-inferred nodes and relationships
    llm_output = get_relationships_from_llm(
        tables=list(table_columns.keys()),
        columns=table_columns,
        fk_relationships=fk_relationships
    )
    print("\nLLM-Inferred Nodes and Relationships:\n", llm_output)
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
    embeddings = create_embeddings_from_descriptions(descriptions)
    print("\nEmbeddings created for all descriptions.")
    return embeddings
    # Optionally: store embeddings in Pinecone/FAISS here

if __name__ == "__main__":
    main()


