import os
import psycopg2
import random
from dotenv import load_dotenv
from faker import Faker


# Load environment variables from the .env file

load_dotenv()

# Parameters for PostgreSQl connection

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Function to connect to the database
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


# Using the get_tasks function
def get_tasks(conn, user_id=None, status_name=None):
    # Get tasks based on user_id, status_name or both
    try:
        with conn.cursor() as cur:
            query = """
                SELECT tasks.id, tasks.title, tasks.description, status.name AS status
                FROM tasks
                JOIN status ON tasks.status_id = status.id
            """
            conditions = []
            params = []

            if user_id:
                conditions.append("tasks.user_id = %s")
                params.append(user_id)

            if status_name:
                conditions.append("status.name = %s")
                params.append(status_name)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cur.execute(query, tuple(params))
            tasks = cur.fetchall()
            if tasks:
                return tasks
            else:
                return None
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []


# Using the update_task_status function
def update_task_status(conn, task_id, new_status_name):
    # Update the status of a task
    try:
        with conn.cursor() as cur:
            # Ensure that the status exists in the 'status' table
            cur.execute("SELECT id FROM status WHERE name = %s", (new_status_name,))
            status = cur.fetchone()

            if status:
                # If the status exists, update the task's status
                status_id = status[0]
                cur.execute("""
                    UPDATE tasks
                    SET status_id = %s
                    WHERE id = %s
                    RETURNING id, title, status_id;
                """, (status_id, task_id))

                updated_task = cur.fetchone()

                if updated_task:
                    print(f"Task ID {updated_task[0]} status updated to {new_status_name}.")
                else:
                    print(f"Task with ID {task_id} not found.")
            else:
                print(f"Status '{new_status_name}' does not exist.")
            conn.commit()
    except Exception as e:
        print(f"Error updating task status: {e}")
        conn.rollback()

# Function to get users without tasks
def get_users_without_tasks(conn):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT users.id, users.fullname
                FROM users
                WHERE users.id NOT IN (
                    SELECT DISTINCT tasks.user_id
                    FROM tasks
                );
            """
            cur.execute(query)
            users = cur.fetchall()
            if users:
                return users
            else:
                return []
    except Exception as e:
        print(f"Error fetching users without tasks: {e}")
        return []


# Function to insert a new task
def insert_task(conn, user_id, title, description, status_name):
    try:
        with conn.cursor() as cur:
            # Ensure that the status exists in the 'status' table
            cur.execute("SELECT id FROM status WHERE name = %s", (status_name,))
            status = cur.fetchone()

            if status:
                status_id = status[0]
                # Insert the new task into the 'tasks' table
                cur.execute("""
                    INSERT INTO tasks (user_id, title, description, status_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, title, description, status_id;
                """, (user_id, title, description, status_id))

                new_task = cur.fetchone()

                if new_task:
                    print(f"For User ID={user_id} added task ID={new_task[0]}, Title={new_task[1]}, Status={status_name}.")
                else:
                    print("Error adding the task.")
            else:
                print(f"Status '{status_name}' does not exist.")

            conn.commit()
    except Exception as e:
        print(f"Error inserting task: {e}")
        conn.rollback()

# Function to get tasks that are not completed
def get_incomplete_tasks(conn):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT tasks.id, tasks.title, tasks.description, status.name AS status
                FROM tasks
                JOIN status ON tasks.status_id = status.id
                WHERE status.name != 'завершено';
            """
            cur.execute(query)
            tasks = cur.fetchall()
            if tasks:
                return tasks
            else:
                return []
    except Exception as e:
        print(f"Error fetching incomplete tasks: {e}")
        return []

# Function to delete a task by id
def delete_task(conn, task_id):
    try:
        with conn.cursor() as cur:
            query = "DELETE FROM tasks WHERE id = %s;"
            cur.execute(query, (task_id,))
            conn.commit()

            if cur.rowcount > 0:
                print(f"Task with ID {task_id} was deleted successfully.")
            else:
                print(f"Task with ID {task_id} not found.")
    except Exception as e:
        print(f"Error deleting task: {e}")
        conn.rollback()

# Function to get users with a certain email pattern
def get_users_by_email(conn, email_pattern):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT users.id, users.fullname, users.email
                FROM users
                WHERE users.email LIKE %s;
            """
            cur.execute(query, (email_pattern,))
            users = cur.fetchall()
            if users:
                return users
            else:
                return []
    except Exception as e:
        print(f"Error fetching users by email: {e}")
        return []

# Function to update user's name
def update_user_name(conn, user_id, new_fullname):
    try:
        with conn.cursor() as cur:
            # Get the current fullname before updating
            cur.execute("SELECT fullname FROM users WHERE id = %s", (user_id,))
            old_fullname = cur.fetchone()

            if old_fullname:
                old_fullname = old_fullname[0]

                # SQL query to update the user's fullname
                query = """
                    UPDATE users
                    SET fullname = %s
                    WHERE id = %s;
                """
                cur.execute(query, (new_fullname, user_id))
                conn.commit()

                print(f"The user with previous fullname '{old_fullname}' was updated to '{new_fullname}'.")
            else:
                print(f"No user found with ID {user_id}.")
    except Exception as e:
        print(f"Error updating user name: {e}")
        conn.rollback()

# Function to get task count for each status
def get_task_count_by_status(conn):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT status.name AS status_name, COUNT(tasks.id) AS task_count
                FROM tasks
                JOIN status ON tasks.status_id = status.id
                GROUP BY status.name;
            """
            cur.execute(query)
            result = cur.fetchall()
            return result
    except Exception as e:
        print(f"Error fetching task counts: {e}")
        return []

def get_tasks_by_email_domain(conn, domain):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT tasks.id, tasks.title, tasks.description, users.email
                FROM tasks
                JOIN users ON tasks.user_id = users.id
                WHERE users.email LIKE %s;
            """
            cur.execute(query, (f"%@{domain}",))
            tasks = cur.fetchall()
            if tasks:
                return tasks
            else:
                return []
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

# Function to get tasks without description
def get_tasks_without_description(conn):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT id, title
                FROM tasks
                WHERE description IS NULL OR description = '';
            """
            cur.execute(query)
            tasks = cur.fetchall()
            if tasks:
                return tasks
            else:
                return []
    except Exception as e:
        print(f"Error fetching tasks without description: {e}")
        return []

def get_users_with_in_progress_tasks(conn):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT users.id, users.fullname, tasks.id AS task_id, tasks.title AS task_title
                FROM users
                INNER JOIN tasks ON users.id = tasks.user_id
                INNER JOIN status ON tasks.status_id = status.id
                WHERE status.name = %s;
            """
            cur.execute(query, ('in_progress',))
            users_with_tasks = cur.fetchall()
            if users_with_tasks:
                return users_with_tasks
            else:
                return []
    except Exception as e:
        print(f"Error fetching users with in progress tasks: {e}")
        return []

def get_users_and_task_count(conn):
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    users.id AS user_id, 
                    users.fullname AS user_fullname, 
                    COUNT(tasks.id) AS task_count
                FROM 
                    users
                LEFT JOIN 
                    tasks ON users.id = tasks.user_id
                GROUP BY 
                    users.id
                ORDER BY 
                    user_fullname;
            """
            cur.execute(query)
            users_task_count = cur.fetchall()

            if users_task_count:
                return users_task_count
            else:
                return None
    except Exception as e:
        print(f"Error fetching users and their task count: {e}")
        return []



conn = create_connection()
if conn:
    user_id = 19                    # For all users, or you can specify a user_id
    task_id = 1                     # Specify the task_id to update
    new_status_name = "in_progress" # Specify the new status ('new', 'in_progress', 'completed')
    print()
    status_name = None              # For a specific status, or you can leave it as None for all statuses

    update_task_status(conn, task_id, new_status_name)
    print("-----------------------------------------------------------------")

    tasks = get_tasks(conn, user_id, status_name)
    if tasks:
        for task in tasks:
            print(f"Task ID: {task[0]}, Title: {task[1]}, Description: {task[2]}, Status: {task[3]}")
    else:
        print(f"No tasks found.")
    print("-----------------------------------------------------------------")

    users_without_tasks = get_users_without_tasks(conn)
    if users_without_tasks:
        print("Users without tasks:")
        print()
        for user in users_without_tasks:
            print(f"User ID: {user[0]}, Name: {user[1]}")
    else:
        print("No users without tasks.")
    print("-----------------------------------------------------------------")

    user_id = 1  # Specify the user_id
    title = f"Next task for Lucky user №{user_id}"  # Task title
    description = "Description of the new task"  # Task description
    status_name = "new"  # Task status (ensure this status exists in the 'status' table)
    insert_task(conn, user_id, title, description, status_name)
    print("-----------------------------------------------------------------")

    incomplete_tasks = get_incomplete_tasks(conn)

    if incomplete_tasks:
        print("Incomplete tasks:")
        for task in incomplete_tasks:
            print(f"Task ID: {task[0]}, Title: {task[1]}, Description: {task[2]}, Status: {task[3]}")
    else:
        print("No incomplete tasks.")
    print("-----------------------------------------------------------------")

    task_id = 1  # Specify the task_id you want to delete
    delete_task(conn, task_id)
    print("-----------------------------------------------------------------")

    email_pattern = "lynn03@example.net"  # Define the email pattern
    users_with_email = get_users_by_email(conn, email_pattern)
    if users_with_email:
        print(f"Users with the given email {email_pattern}:")
        for user in users_with_email:
            print(f"User ID: {user[0]}, \nUsername: {user[1]}, \nEmail: {user[2]}")
    else:
        print("No users found with the given email pattern.")
    print("-----------------------------------------------------------------")

    user_id = 1  # The ID of the user whose name you want to update
    new_fullname = "Elizabeth Dixon_Smith"  # The new name you want to set
    update_user_name(conn, user_id, new_fullname)
    print("-----------------------------------------------------------------")

    task_counts = get_task_count_by_status(conn)
    if task_counts:
        print("Task counts by status:")
        for status_name, task_count in task_counts:
            print(f"Status: {status_name}, Task Count: {task_count}")
    else:
        print("No task counts found.")
    print("-----------------------------------------------------------------")

    domain = "gmail.com"  # Specify the domain
    tasks = get_tasks_by_email_domain(conn, domain)
    if tasks:
        print(f"Tasks for users with email domain {domain}:")
        for task in tasks:
            print(f"Task ID: {task[0]}, Title: {task[1]}, Description: {task[2]}, User Email: {task[3]}")
    else:
        print(f"No tasks found for users with email domain '@{domain}'.")
    print("-----------------------------------------------------------------")

    tasks_without_description = get_tasks_without_description(conn)
    if tasks_without_description:
        print("Tasks without description:")
        for task in tasks_without_description:
            print(f"Task ID: {task[0]}, Title: {task[1]}")
    else:
        print("No tasks without description.")
    print("-----------------------------------------------------------------")

    users_with_in_progress = get_users_with_in_progress_tasks(conn)
    if users_with_in_progress:
        print("Users with in progress tasks:")
        for user in users_with_in_progress:
            print(f"User ID: {user[0]}, Name: {user[1]}, Task ID: {user[2]}, Task Title: {user[3]}")
    else:
        print("No users with in progress tasks.")
    print("-----------------------------------------------------------------")

    users_task_count = get_users_and_task_count(conn)
    if users_task_count:
        print("All users and their tasks count:")
        print()
        for user in users_task_count:
            print(f"User ID: {user[0]}, User Name: {user[1]}, Task Count: {user[2]}")
    else:
        print("No users found.")
    print("-----------------------------------------------------------------")

    conn.close()
