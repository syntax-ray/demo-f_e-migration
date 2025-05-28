import os
import psycopg2
import pyodbc
from psycopg2.extras import execute_values


source_db = {
    "host": os.getenv("DEMO_SOURCE_HOST", 'localhost'),
    "port": os.getenv("DEMO_SOURCE_PORT"),
    "user": os.getenv("DEMO_SOURCE_USER"),
    "password": os.getenv("DEMO_SOURCE_PASSWORD"),
    "database": os.getenv("DEMO_SOURCE_DB")
}  

migration_db = {
    "host": os.getenv("MG_SERVER_HOST", 'localhost'),
    "port": os.getenv("MG_SERVER_PORT", 5432),
    "user": os.getenv("MG_SERVER_USER"),
    "password": os.getenv("MG_SERVER_PASSWORD"),
    "database": os.getenv("MG_SERVER_DB", 'postgres')
} 

FULL_MIGRATION = True
BATCH_SIZE = 10000 # Number of rows to insert in each migration batch
MSSQL_ODBC_DRIVER = 'ODBC Driver 18 for SQL Server'


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
            database= migration_db["database"]
        )
        print("Successfully connected to the migration server database.")  # Simple query to check connection
        return True, conn
    except Exception as e:
        print("Failed to connect to the migration server database with the provided credentials.")
        print(f"Connection failed: {e}")
        return False, None
    

def test_source_db_connection():
    conn_str = f'DRIVER={MSSQL_ODBC_DRIVER};SERVER={source_db["host"]}; \
                 UID={source_db["user"]};PWD={source_db["password"]};PORT={source_db["port"]}; \
                 DATABASE={source_db["database"]};TrustServerCertificate=yes;'

    try:
        conn = pyodbc.connect(conn_str)
        print("Successfully connected to the source database.")
        return True, conn
    except Exception as e:
        print("Failed to connect to the source database with the provided credentials.")
        print(f"Connection failed: {e}")
        return False, None
    

def get_source_db_tables(conn):
    table_list = []
    query = '''
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            '''
    tables = conn.execute(query).fetchall()
    for table_tuple in tables:
        schema, table = table_tuple
        table_list.append(f'{schema}.{table}') 
    return table_list


def close_db_connections(source_conn, migration_conn):
    source_conn.close()
    migration_conn.close()


def map_sqlserver_to_postgres_type(sql_type):
    mapping = {
        'bigint': 'bigint',
        'varchar': 'text',
        'date': 'date',
        'bit': 'boolean',
        'money': 'numeric(19,4)',
        'datetime': 'timestamp',
        'int': 'integer'
    }
    return mapping.get(sql_type.lower(), None)


def create_postgres_tables_from_sqlserver(source_conn,migration_server_conn,tables):
    for table in tables:
        mirgation_server_table_name = f"{table.split('.')[0]}_{table.split('.')[-1]}"
        source_db_schema = table.split('.')[0]
        source_db_table_name = table.split('.')[-1]
        table_present = 0
        with migration_server_conn.cursor() as cursor:
            cursor.execute(f"select count(*) FROM information_schema.tables where lower(table_type) = 'base table' and lower(table_schema) = 'public' and table_name = '{mirgation_server_table_name}'")
            result = cursor.fetchone()
            table_present = result[0]
        if table_present:
            print(f"Table {mirgation_server_table_name} already exists in the migration database. Skipping creation.")
            continue
        else:
            print(f"Creating table {mirgation_server_table_name} in the migration database.")
            columns = source_conn.execute(f"select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{source_db_table_name}' and lower(TABLE_SCHEMA) = '{source_db_schema}'").fetchall()
            col_defs = []
            for col in columns:
                postgres_datatype = map_sqlserver_to_postgres_type(col[1])
                if not postgres_datatype:
                    print(f"Unmapped source db column datatype: {col[1]}")
                    print("Add this mapping to the map_sqlserver_to_postgres_type function to proceed")
                    exit(1)
                else:
                    col_defs.append(f"{col[0]} {postgres_datatype}")
            if col_defs:
                create_table_query = f"CREATE TABLE IF NOT EXISTS {mirgation_server_table_name} ({', '.join(col_defs)});"
                with migration_server_conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    migration_server_conn.commit()
                print(f"Table {mirgation_server_table_name} created successfully in the migration database.")
            create_table_query = f"CREATE TABLE {mirgation_server_table_name} ({', '.join(col_defs)});"


def migrate_table_data(source_conn, migration_conn, tables):
    for table in tables:
        mirgation_server_table_name = f"{table.split('.')[0]}_{table.split('.')[-1]}"
        print(f"Migrating data for table {mirgation_server_table_name}")
        table_cols = None
        with migration_conn.cursor() as cursor:
            get_cols_query = f"select column_name from information_schema.columns where table_name = '{mirgation_server_table_name}'"
            cursor.execute(get_cols_query)
            result = cursor.fetchall()
            table_cols = ",".join([f"{col_tuple[0]}" for col_tuple in result]).strip()
            # clear the table before inserting new data
            cursor.execute(f"delete from {mirgation_server_table_name}")
        insert_sql = f'INSERT INTO {mirgation_server_table_name} ({table_cols}) VALUES %s'
        offset = 0
        while True:
            rows = source_conn.execute(
                    f"SELECT {table_cols} FROM {table} ORDER BY 1 OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", 
                    offset, BATCH_SIZE
            ).fetchall()
            if not rows:
                break
            with migration_conn.cursor() as cursor:
                execute_values(cursor, insert_sql, rows)
                migration_conn.commit()
            offset += BATCH_SIZE
        print(f"Finished migrating {mirgation_server_table_name} table data")
    print("Data migration completed for all tables.")
    
        

if __name__ == "__main__":
    migration_sever_conn_ok, migration_server_conn = test_migration_server_db_connection()
    source_db_conn_ok, source_db_conn = test_source_db_connection()
    if (migration_sever_conn_ok and source_db_conn_ok):
        if FULL_MIGRATION:
            all_tables = get_source_db_tables(source_db_conn)
            if not all_tables:
                print("Source database has no tables: nothing to migrate")
                close_db_connections(source_db_conn, migration_server_conn)
                exit(1)
            else:
                print(f'Source db tables found {all_tables}')
            create_postgres_tables_from_sqlserver(source_db_conn, migration_server_conn, all_tables)
            migrate_table_data(source_db_conn, migration_server_conn, all_tables)
        close_db_connections(source_db_conn, migration_server_conn)
    else:
        close_db_connections(source_db_conn, migration_server_conn)
        exit(1)