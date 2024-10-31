import pandas as pd
import pyodbc
import psycopg2
from psycopg2.extras import execute_values
from vanna.ollama import Ollama
from vanna.base import VannaBase
import numpy as np
import requests

class CustomVectorDB(VannaBase):
    def __init__(self, config=None):
        super().__init__(config)
        # Vector DB connection
        self.vector_conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="Wx1a6Tq4B1CmghMYShi5N65015Q40SxY"
        )
        
        # Create necessary tables if they don't exist
        self._initialize_tables()

    def _initialize_tables(self):
        with self.vector_conn.cursor() as cur:
            # Create tables for storing embeddings and training data
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ddl_store (
                    id SERIAL PRIMARY KEY,
                    ddl_text TEXT,
                    embedding vector(1024)  -- Adjust vector size based on your model
                );
                
                CREATE TABLE IF NOT EXISTS documentation_store (
                    id SERIAL PRIMARY KEY,
                    doc_text TEXT,
                    embedding vector(1024)
                );
                
                CREATE TABLE IF NOT EXISTS question_sql_store (
                    id SERIAL PRIMARY KEY,
                    question TEXT,
                    sql_query TEXT,
                    embedding vector(1024)
                );
            """)
            self.vector_conn.commit()

    def generate_embedding(self, text: str, **kwargs) -> list:
        """
        Generate embeddings for the given text using the configured model.
        Required implementation for VannaBase abstract method.
        """
        # Using Ollama's embedding endpoint
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": text}
        )
        
        if response.status_code == 200:
            embedding = response.json().get('embedding', [])
            return embedding
        else:
            raise Exception(f"Failed to generate embedding: {response.text}")

    def add_ddl(self, ddl: str, **kwargs) -> str:
        # Store DDL with its embedding
        embedding = self.generate_embedding(ddl)
        with self.vector_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ddl_store (ddl_text, embedding) VALUES (%s, %s) RETURNING id",
                (ddl, embedding)
            )
            id = cur.fetchone()[0]
            self.vector_conn.commit()
        return str(id)

    def add_documentation(self, doc: str, **kwargs) -> str:
        embedding = self.generate_embedding(doc)
        with self.vector_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documentation_store (doc_text, embedding) VALUES (%s, %s) RETURNING id",
                (doc, embedding)
            )
            id = cur.fetchone()[0]
            self.vector_conn.commit()
        return str(id)

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO question_sql_store (question, sql_query, embedding) VALUES (%s, %s, %s) RETURNING id",
                (question, sql, embedding)
            )
            id = cur.fetchone()[0]
            self.vector_conn.commit()
        return str(id)

    def get_related_ddl(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT ddl_text, 1 - (embedding <=> %s) as similarity 
                FROM ddl_store 
                ORDER BY similarity DESC 
                LIMIT 5
            """, (embedding,))
            return [row[0] for row in cur.fetchall()]

    def get_related_documentation(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT doc_text, 1 - (embedding <=> %s) as similarity 
                FROM documentation_store 
                ORDER BY similarity DESC 
                LIMIT 5
            """, (embedding,))
            return [row[0] for row in cur.fetchall()]

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT question, sql_query, 1 - (embedding <=> %s) as similarity 
                FROM question_sql_store 
                ORDER BY similarity DESC 
                LIMIT 5
            """, (embedding,))
            return [(row[0], row[1]) for row in cur.fetchall()]

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT 'ddl' as type, id, ddl_text as text FROM ddl_store
                UNION ALL
                SELECT 'documentation' as type, id, doc_text as text FROM documentation_store
                UNION ALL
                SELECT 'question_sql' as type, id, question || ' | ' || sql_query as text FROM question_sql_store
            """)
            return pd.DataFrame(cur.fetchall(), columns=['type', 'id', 'text'])

    def remove_training_data(self, id: str, **kwargs) -> bool:
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                DELETE FROM ddl_store WHERE id = %s;
                DELETE FROM documentation_store WHERE id = %s;
                DELETE FROM question_sql_store WHERE id = %s;
            """, (id, id, id))
            self.vector_conn.commit()
            return True

class MyVanna(CustomVectorDB, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Ensure model is specified
        if 'model' not in config:
            config['model'] = 'mxbai-embed-large'
            
        CustomVectorDB.__init__(self, config=config)
        Ollama.__init__(self, config=config)
        
        try:
            self.sql_conn = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost;"
                "DATABASE=kpdb;"
                "Trusted_Connection=yes;"
            )
            self.run_sql_is_set = True
        except pyodbc.Error as e:
            raise ConnectionError(f"Failed to connect to SQL Server: {str(e)}")

    def run_sql(self, sql: str) -> pd.DataFrame:
        return pd.read_sql_query(sql, self.sql_conn)

# Initialize Vanna with Mistral model
vn = MyVanna(config={'model': 'mxbai-embed-large'})