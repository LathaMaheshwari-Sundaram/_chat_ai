import sqlite3
import pandas as pd
from groq import Groq
from config import config

# Initialize the Groq client with your API key
client = Groq(api_key=config.GROQ_API_KEY)

def get_db_schema():
    """
    Connects to the SQLite database and retrieves all table and column information.
    Returns a formatted string for the LLM.
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get a list of all table names in our company database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = "The database has the following tables and columns:\n"
    
    # Loop through each table to find its columns
    for table in tables:
        table_name = table[0]
        schema_info += f"- Table: {table_name}\n"
        
        # PRAGMA table_info gives us column names and data types (e.g. TEXT, REAL)
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            schema_info += f"  - Column: {col[1]} ({col[2]})\n"
            
    conn.close()
    return schema_info

def run_text_to_sql(user_question):
    """
    Converts a natural language question into a SQL query and runs it.
    Returns the results of the query or an error message.
    """
    # Step 1: Get the current database structure
    schema = get_db_schema()

    # Step 2: Ask Groq LLM to write the SQL query based on the question and schema
    prompt = (f"{schema}\n\n"
              f"User Question: {user_question}\n"
              "Write a SQL query that answers this question. Return ONLY the SQL query. "
              "Do not use markdown backticks, explanations, or any other text.")

    completion = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0 # Use 0 for consistent SQL generation
    )
    
    sql_query = completion.choices[0].message.content.strip()

    # Step 3: Run the generated SQL query safely on the database using pandas
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
        # Use pandas to read the SQL results directly into a DataFrame
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        # Step 4: Format the results into a string for the chatbot response
        if df.empty:
            return f"Query returned no results. SQL used: {sql_query}"
        return f"SQL Query: {sql_query}\n\nResults:\n{df.to_string(index=False)}"
    
    except Exception as e:
        # Return the error message and the attempted query if it fails
        return f"Database Error: {str(e)}. Attempted SQL: {sql_query}"
