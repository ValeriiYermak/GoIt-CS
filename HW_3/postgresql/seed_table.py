import os
import psycopg2
from dotenv import load_dotenv
from faker import Faker
import random

# Load environment variables from the .env file

load_dotenv()

# Parameters for PostgreSQl connection

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

num_users = 30
statuses = ["new", "in_progress", "completed"]
num_tasks = 10

# Create a Faker instance

fake = Faker()


def create_connection():
    # Connects to the 'hw3' database
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connection to the '{DB_NAME}' database: {e}")
        return None


def insert_random_users(conn, num_users):
    # Insert random users into the users table.
    with conn.cursor() as cur:
        for _ in range(num_users):
            fullname = fake.name()
            email = fake.email()
            cur.execute(
                "INSERT INTO users (fullname, email) VALUES (%s, %s) RETURNING id;",
                (fullname, email),
            )
            user_id = cur.fetchone()[0]
            print(f"Inserted user {fullname} with ID {user_id}.")
        conn.commit()


def insert_random_status(conn, statuses):
    # Insert random statuses into the status table.
    with conn.cursor() as cur:
        for status in statuses:
            cur.execute(
                "INSERT INTO status (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                (status,),
            )
        conn.commit()
        print(f"Inserted statuses: {','.join(statuses)}.")


def insert_random_tasks(conn, num_tasks):
    # Insert random tasks into the tasks table.
    with conn.cursor() as cur:
        for _ in range(num_tasks):
            title = fake.sentence(nb_words=3)
            description = fake.text()
            status_id = random.randint(1, len(statuses))
            user_id = random.randint(1, num_users)
            cur.execute(
                "INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s);",
                (title, description, status_id, user_id),
            )
            print(f"Inserted task: {title}.")
        conn.commit()


if __name__ == "__main__":
    # 1. Connect to the hw3 database
    conn = create_connection()
    if conn:
        # 2. Insert random users into the 'users' table
        insert_random_users(conn, num_users)

        # 3. Insert random statuses into the 'status' table
        insert_random_status(conn, statuses)
        # 4. Insert random tasks into the 'tasks' table
        insert_random_tasks(conn, num_tasks)
        # 5. Close the connection
        conn.close()
    else:
        print(f"Error! Could not connect to the 'hw3' database.")
