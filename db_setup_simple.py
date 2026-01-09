import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='backend/.env')

def test_connection():
    """Test the connection to the Neon PostgreSQL database"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            print("ERROR: DATABASE_URL not found in .env file")
            return False

        print(f"Testing connection to: {database_url}")

        # Connect directly using the full database URL
        conn = psycopg2.connect(database_url)

        # Set autocommit to allow CREATE TABLE statements
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("SUCCESS: Connected to Neon PostgreSQL database!")

        # Test the connection with a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Database version: {db_version[0][:50]}...")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

def create_tables():
    """Create the users and todos tables in the database"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            print("ERROR: DATABASE_URL not found in .env file")
            return False

        # Connect directly using the full database URL
        conn = psycopg2.connect(database_url)

        # Set autocommit to allow CREATE TABLE statements
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("\nCreating tables...")

        # Drop tables if they exist (optional, for clean setup)
        drop_tables = [
            "DROP TABLE IF EXISTS todos;",
            "DROP TABLE IF EXISTS users;"
        ]

        for drop_sql in drop_tables:
            try:
                cursor.execute(drop_sql)
                print("  Removed existing table if it existed")
            except:
                pass  # Ignore errors if tables don't exist

        # SQL to create the users table
        create_users_table = """
        CREATE TABLE users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # SQL to create the todos table
        create_todos_table = """
        CREATE TABLE todos (
            id VARCHAR(36) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Execute the table creation
        cursor.execute(create_users_table)
        print("SUCCESS: Created 'users' table")

        cursor.execute(create_todos_table)
        print("SUCCESS: Created 'todos' table")

        # Insert a test user to verify everything works
        import uuid
        test_user_id = str(uuid.uuid4())
        insert_test_user = """
        INSERT INTO users (id, email, password)
        VALUES (%s, %s, %s);
        """
        cursor.execute(insert_test_user, (test_user_id, 'test@example.com', 'hashed_password'))
        print("SUCCESS: Inserted test data to verify tables work")

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

        print("\nDatabase setup completed successfully!")
        print("SUCCESS: Users table created with columns: id, email, password, created_at, updated_at")
        print("SUCCESS: Todos table created with columns: id, title, description, completed, user_id, created_at, updated_at")

        return True

    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

def main():
    """Main function to run the database setup"""
    print("Starting Neon PostgreSQL database setup...")
    print("=" * 50)

    # Test the connection first
    if not test_connection():
        print("\nCannot proceed without database connection")
        return

    # Create the tables
    create_tables()

    print("\n" + "=" * 50)
    print("Next steps:")
    print("   - Your database is now ready with users and todos tables")
    print("   - Run your backend server with: cd backend && uvicorn src.api.main:app --reload")
    print("   - The application will now be able to store user accounts and todos")

if __name__ == "__main__":
    main()