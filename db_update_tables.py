import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import uuid
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv(dotenv_path='backend/.env')

def recreate_tables():
    """Recreate the user and todo tables to match SQLModel expectations"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            print("ERROR: DATABASE_URL not found in .env file")
            return False

        # Parse the database URL using urlparse
        parsed = urlparse(database_url)

        if not parsed.hostname:
            print("ERROR: Could not parse database URL")
            return False

        # Connect to the database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password
        )

        # Set autocommit to allow CREATE TABLE statements
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("\nRecreating tables to match SQLModel schema...")

        # Drop tables if they exist
        drop_tables = [
            "DROP TABLE IF EXISTS todos;",
            "DROP TABLE IF EXISTS todo;",  # In case of plural/singular confusion
            "DROP TABLE IF EXISTS users;",
            "DROP TABLE IF EXISTS user;"   # SQLModel typically uses singular form
        ]

        for drop_sql in drop_tables:
            try:
                cursor.execute(drop_sql)
                print(f"  Dropped table if it existed")
            except:
                pass  # Ignore errors if tables don't exist

        # SQL to create the user table (matching SQLModel expectation - singular form)
        create_user_table = """
        CREATE TABLE "user" (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # SQL to create the todo table (matching SQLModel expectation - singular form)
        create_todo_table = """
        CREATE TABLE "todo" (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            user_id VARCHAR(36) REFERENCES "user"(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Execute the table creation
        cursor.execute(create_user_table)
        print("Created 'user' table")

        cursor.execute(create_todo_table)
        print("Created 'todo' table")

        # Insert a test user to verify everything works
        test_user_id = str(uuid.uuid4())
        insert_test_user = """
        INSERT INTO "user" (id, email, password)
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_test_user, (test_user_id, 'test@example.com', 'hashed_password'))
        print("Inserted test data to verify tables work")

        # Verify tables were created
        cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print(f"\nTables in database: {[table[0] for table in tables]}")

        cursor.close()
        conn.close()

        print("\nDatabase tables recreated successfully!")
        print("User table created with columns: id, email, password, created_at, updated_at")
        print("Todo table created with columns: id, title, description, completed, user_id, created_at, updated_at")

        return True

    except Exception as e:
        print(f"Error recreating tables: {str(e)}")
        return False

def main():
    """Main function to run the database recreation"""
    print("Recreating database tables to match SQLModel schema...")
    print("=" * 60)

    recreate_tables()

    print("\n" + "=" * 60)
    print("Database is now ready with correct table names for SQLModel.")

if __name__ == "__main__":
    main()