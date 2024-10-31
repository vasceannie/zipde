import pandas as pd
import pyodbc
import psycopg2
from psycopg2.extras import execute_values
from vanna.ollama import Ollama
from vanna.base import VannaBase
import numpy as np
import requests
from vanna.flask import VannaFlaskApp
from vanna.vannadb import VannaDB_VectorStore


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
                SELECT ddl_text, 1 - (embedding <-> %s::vector) as similarity 
                FROM ddl_store 
                ORDER BY similarity DESC 
                LIMIT 5
            """, (embedding,))
            return [row[0] for row in cur.fetchall()]

    def get_related_documentation(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT doc_text, 1 - (embedding <-> %s::vector) as similarity 
                FROM documentation_store 
                ORDER BY similarity DESC 
                LIMIT 5
            """, (embedding,))
            return [row[0] for row in cur.fetchall()]

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT question, sql_query, 1 - (embedding <-> %s::vector) as similarity 
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

class MyCustomLLM(VannaBase):
    def __init__(self, config=None):
        super().__init__(config)
        self.model = config.get('model', 'llama3.2')  # Default model
        
    def system_message(self) -> str:
        return "You are a helpful AI assistant that generates SQL queries and helps users interpret data."
        
    def user_message(self, message: str) -> str:
        return f"User: {message}"
        
    def assistant_message(self, message: str) -> str:
        return f"Assistant: {message}"

    def submit_prompt(self, prompt, **kwargs) -> str:
        # Implement Ollama chat functionality
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": self.model, "messages": [
                {"role": "system", "content": self.system_message()},
                {"role": "user", "content": prompt}
            ]}
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"Failed to get response: {response.text}")

class MyVanna(CustomVectorDB, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}
            
        self.config = config
        self.max_tokens = 4096
        self.static_documentation = ""
            
        # Initialize both parent classes
        CustomVectorDB.__init__(self, config)
        Ollama.__init__(self, config)

    def submit_prompt(self, prompt, **kwargs) -> str:
        # Format the prompt properly for Ollama
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that generates SQL queries."},
            {"role": "user", "content": prompt if isinstance(prompt, str) else prompt[-1]}
        ]
        
        # Make the API call
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": self.config.get('model', 'llama3.2'), 
                  "messages": messages}
        )
        
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"Failed to get response: {response.text}")

    def get_sql_prompt(self, question: str, question_sql_list: list, ddl_list: list, doc_list: list, **kwargs):
        prompt = f"""Given the following question: {question}

Related DDL:
{' '.join(ddl_list)}

Related documentation:
{' '.join(doc_list)}

Similar questions and their SQL:
{' '.join([f'Q: {q} A: {sql}' for q, sql in question_sql_list])}

Generate a SQL query to answer the question."""
        return prompt

    def get_followup_questions_prompt(self, question: str, question_sql_list: list, ddl_list: list, doc_list: list, **kwargs):
        prompt = f"""Based on the question "{question}", suggest 3 relevant follow-up questions."""
        return prompt

# Initialize Vanna with the correct model name
vn = MyVanna(config={
    'model': 'llama3.2'
})

# Connect to MSSQL using the proper connection string format
vn.connect_to_mssql(
    odbc_conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE=kpdb;Trusted_Connection=yes"
)

# Initialize Flask app
flask_app = VannaFlaskApp(
    vn=vn, 
    allow_llm_to_see_data=True, 
    logo='banner-logo-rise-now2x.png', 
    title='Database Deblunker', 
    subtitle='Deblunk that base of data real good.'
)
flask_app.run()
