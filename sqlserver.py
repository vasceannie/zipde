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
                CREATE TABLE IF NOT EXISTS vanna_ddl_store (
                    id SERIAL PRIMARY KEY,
                    ddl_text TEXT,
                    embedding vector(1024)  -- Adjust vector size based on your model
                );
                
                CREATE TABLE IF NOT EXISTS vanna_documentation_store (
                    id SERIAL PRIMARY KEY,
                    doc_text TEXT,
                    embedding vector(1024)
                );
                
                CREATE TABLE IF NOT EXISTS vanna_question_sql_store (
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
                "INSERT INTO vanna_ddl_store (ddl_text, embedding) VALUES (%s, %s) RETURNING id",
                (ddl, embedding)
            )
            id = cur.fetchone()[0]
            self.vector_conn.commit()
        return str(id)

    def add_documentation(self, doc: str, **kwargs) -> str:
        embedding = self.generate_embedding(doc)
        with self.vector_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO vanna_documentation_store (doc_text, embedding) VALUES (%s, %s) RETURNING id",
                (doc, embedding)
            )
            id = cur.fetchone()[0]
            self.vector_conn.commit()
        return str(id)

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO vanna_question_sql_store (question, sql_query, embedding) VALUES (%s, %s, %s) RETURNING id",
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
                FROM vanna_ddl_store 
                ORDER BY similarity DESC 
                LIMIT 10
            """, (embedding,))
            return [row[0] for row in cur.fetchall()]

    def get_related_documentation(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT doc_text, 1 - (embedding <-> %s::vector) as similarity 
                FROM vanna_documentation_store 
                ORDER BY similarity DESC 
                LIMIT 10
            """, (embedding,))
            return [row[0] for row in cur.fetchall()]

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        embedding = self.generate_embedding(question)
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT question, sql_query, 1 - (embedding <-> %s::vector) as similarity 
                FROM vanna_question_sql_store 
                ORDER BY similarity DESC 
                LIMIT 10
            """, (embedding,))
            return [(row[0], row[1]) for row in cur.fetchall()]

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                SELECT 'ddl' as type, id, ddl_text as text FROM vanna_ddl_store
                UNION ALL
                SELECT 'documentation' as type, id, doc_text as text FROM vanna_documentation_store
                UNION ALL
                SELECT 'question_sql' as type, id, question || ' | ' || sql_query as text FROM vanna_question_sql_store
            """)
            return pd.DataFrame(cur.fetchall(), columns=['type', 'id', 'text'])

    def remove_training_data(self, id: str, **kwargs) -> bool:
        with self.vector_conn.cursor() as cur:
            cur.execute("""
                DELETE FROM vanna_ddl_store WHERE id = %s;
                DELETE FROM vanna_documentation_store WHERE id = %s;
                DELETE FROM vanna_question_sql_store WHERE id = %s;
            """, (id, id, id))
            self.vector_conn.commit()
            return True

class MyCustomLLM(VannaBase):
    def __init__(self, config=None):
        super().__init__(config)
        self.model = config.get('model', 'llama3.2')  # Default model
        
    def system_message(self) -> str:
        return (
            "The user will provide SQL queries or questions for you to convert into SQL syntax. "
            "You are working with Microsoft SQL Server, so make sure to wrap all table names and column names "
            "in square brackets [ ] to handle spaces, special characters, or reserved keywords. "
            "For example, convert `Contract #` to `[Contract #]`. "
            "If the user requests information, guess the business question being answered by the query "
            "without referencing specific table names in the response."
        )
        
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
            config = {
                'model': 'llama3.2'
            }
            
        self.connect_to_mssql(
            odbc_conn_str=f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE=kpdb;Trusted_Connection=yes"
        )    
        self.config = config
        self.max_tokens = 4096
        self.static_documentation = ""
            
        # Initialize both parent classes
        CustomVectorDB.__init__(self, config)
        Ollama.__init__(self, config)

    def system_message(self, message: str = None) -> str:
        # If a message is provided, use it, otherwise use default
        if message:
            return message
        return (
            "The user will provide SQL queries or questions for you to convert into SQL syntax. ",
            "You are working with Microsoft SQL Server, so make sure to wrap all table names and column names ",
            "in square brackets [ ] to handle spaces, special characters, or reserved keywords. ",
            "For example, convert `Contract #` to `[Contract #]`. ",
            "If the user requests information, guess the business question being answered by the query ",
            "without referencing specific table names in the response."
        )
        
    def user_message(self, message: str) -> str:
        return f"User: {message}"
        
    def assistant_message(self, message: str) -> str:
        return f"Assistant: {message}"

    def submit_prompt(self, prompt, **kwargs) -> str:
        try:
            # Format the messages properly
            if isinstance(prompt, list):
                messages = prompt
            else:
                messages = [
                    {
                        "role": "system",
                        "content": self.system_message()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

            # Make the API call
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.config.get('model', 'llama3.2'),
                    "messages": messages,
                    "stream": True
                }
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get('response', '')
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    return response.text
            else:
                raise Exception(f"API call failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Error in submit_prompt: {str(e)}")
            raise

    def get_sql_prompt(self, question: str, question_sql_list: list, ddl_list: list, doc_list: list, **kwargs):
        prompt = f"""Given the following question: {question}

            Related DDL:
            {' '.join(ddl_list)}

            Related documentation:
            {' '.join(doc_list)}

            Similar questions and their SQL:
            {' '.join([f'Q: {q} A: {sql}' for q, sql in question_sql_list])}

            Generate a SQL query to answer the question.
            """
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
