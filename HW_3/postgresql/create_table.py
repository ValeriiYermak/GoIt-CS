import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Parameters for PostgreSQL connection
# Use "postgres" as the database name for administrative tasks (creating new databases, etc.)
DB_NAME = os.getenv(
    "DB_NAME"
)  # DB_NAME is now set to "postgres" for administrative tasks
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def create_database():
    """Connects to the PostgreSQL system database (postgres) and creates the `hw3` database if it doesn't exist."""
    conn = None
    try:
        # Connect to the PostgreSQL system database "postgres" for administrative tasks
        conn = psycopg2.connect(
            dbname="postgres",  # Initially connecting to the "postgres" system database
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True  # Enable autocommit so that we can create databases
        cur = conn.cursor()

        # Check if the "hw3" database already exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
        exists = cur.fetchone()

        if not exists:
            # Create the "hw3" database if it doesn't exist
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database `{DB_NAME}` created successfully.")
        else:
            print(f"Database `{DB_NAME}` already exists.")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Error while creating the database: {e}")
    finally:
        if conn:
            conn.close()


def create_connection():
    """Connects to the newly created `hw3` database (after it's created)."""
    try:
        # Connect to the newly created `hw3` database
        conn = psycopg2.connect(
            dbname=DB_NAME,  # Now we use DB_NAME which is "hw3" after the database is created
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the `{DB_NAME}` database: {e}")
        return None


def create_sql_table():
    """Generates an SQL script and saves it in the current directory as `hw3.sql`."""
    sql_script = """
    CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
    DEFAULT 'new' CHECK (name IN ('new', 'in_progress', 'completed'))
    );
    CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    status_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES status(id),
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    sql_file_path = "hw3.sql"
    with open(sql_file_path, "w") as file:
        file.write(sql_script)
    print(f"SQL script saved to the file {sql_file_path}.")
    return sql_file_path


def execute_sql_file(conn, sql_file_path):
    """Executes the SQL script from the file `hw3.sql`."""
    try:
        with conn.cursor() as cur:
            with open(sql_file_path, "r") as file:
                sql_script = file.read()
                queries = sql_script.split(";")
                for query in queries:
                    query = query.strip()
                    if query:
                        cur.execute(query)
            print("SQL script executed successfully.")
    except Exception as e:
        print(f"Error executing the SQL script: {e}")


if __name__ == "__main__":
    # 1. Create the `hw3` database if it doesn't exist
    create_database()

    # 2. Create the SQL script file `hw3.sql`
    sql_file_path = create_sql_table()

    # 3. Connect to the newly created `hw3` database
    conn = create_connection()
    if conn:
        # 4. Execute the SQL script to create tables
        execute_sql_file(conn, sql_file_path)
        conn.close()
    else:
        print("Error! Could not connect to the `hw3` database.")
