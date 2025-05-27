import os
import psycopg2
import pyodbc


source_db = {
    "host": os.getenv("DEMO_SOURCE_HOST", 'localhost'),
    "port": os.getenv("DEMO_SOURCE_PORT"),
    "user": os.getenv("DEMO_SOURCE_USER"),
    "password": os.getenv("DEMO_SOURCE_PASSWORD")
}  

migration_db = {
    "host": os.getenv("MG_SERVER_HOST", 'localhost'),
    "port": os.getenv("MG_SERVER_PORT", 5432),
    "user": os.getenv("MG_SERVER_USER"),
    "password": os.getenv("MG_SERVER_PASSWORD")
}  


def test_migration_server_db_connection():
    """
    Test the database connection using the provided credentials.
    """
    try:
        conn = psycopg2.connect(
            host=migration_db["host"],
            port=migration_db["port"],
            user=migration_db["user"],
            password=migration_db["password"],
            database="postgres"
        )
        conn.close()
        print("Successfully connected to the migration server database.")
        return True
    except Exception as e:
        print("Failed to connect to the migration server database with the provided credentials.")
        print(f"Connection failed: {e}")
        return False
    
def test_source_db_connection():
    conn_str = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={source_db["host"]}; \
                 UID={source_db["user"]};PWD={source_db["password"]};PORT={source_db["port"]}; \
                TrustServerCertificate=yes;'

    try:
        conn = pyodbc.connect(conn_str)
        conn.close()
        print("Successfully connected to the source database.")
        return True
    except Exception as e:
        print("Failed to connect to the source database with the provided credentials.")
        print(f"Connection failed: {e}")
        return False



if __name__ == "__main__":
    if (test_migration_server_db_connection() and test_source_db_connection()):
        pass
    else:
        exit(1)    
    # print(migration_db)