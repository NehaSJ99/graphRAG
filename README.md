# GraphRAG

A Retrieval-Augmented Generation (RAG) pipeline that connects Databricks SQL tables and Neo4j graph database for advanced context retrieval and LLM-powered question answering.

## Features
- Extracts schema from Databricks SQL tables
- Builds a knowledge graph in Neo4j (tables, columns, relationships)
- Enables context-rich retrieval for LLMs

## Requirements
- Python 3.8+
- Databricks SQL Warehouse access
- Neo4j Aura or self-hosted instance

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/NehaSJ99/graphRAG.git
   ```

2. **Create and activate a virtual environment (recommended):**
   ```sh
   python -m venv graphrag-env
   .\graphrag-env\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in your Databricks and Neo4j credentials, or edit `.env` directly.

## Usage

### 1. Extract and Print Databricks Schema
Run:
```sh
python conn_databricks.py
```
This will print all tables and their schema from your Databricks SQL warehouse.

### 2. Build Graph in Neo4j
Run:
```sh
python create_graph.py
```
This will create nodes for tables and columns, and relationships in your Neo4j database.

### 3. Query Neo4j
You can use `conn_graphdb.py` or your own scripts to run Cypher queries against the graph.

