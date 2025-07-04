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
# Edit to set tables to exclude. FULL_MIGRATION varible should be set to false. Should be formatted as schema."table".  
# The examples of table names are: {'dbo."Project Details"', 'dbo."Employee Records"', 'dbo."loan"'}
# It is formatted this way to handle weird table names ie: table names with spaces
EXCLUSION_SET = set()
# Edit to set tables to include. FULL_MIGRATION varible should be set to false. Should be formatted as schema."table". 
# The examples of table names are: {'dbo."Project Details"', 'dbo."Employee Records"', 'dbo."loan"'}
# It is formatted this way to handle weird table names ie: table names with spaces
INCLUSION_SET = set()


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
        table_name = f'{schema}."{table}"'
        if FULL_MIGRATION:
            table_list.append(table_name) 
        else:    
            if table_name not in EXCLUSION_SET:
                if not INCLUSION_SET:
                    table_list.append(table_name) 
                else:
                    if table_name in INCLUSION_SET:
                        table_list.append(table_name)
            else:
                print(f"Exluding {table_name} from migration")
    return table_list

def generate_postgres_name(name:str):
    return "_".join(name.replace('"', "").strip().lower().split())

def close_db_connections(source_conn, migration_conn):
    source_conn.close()
    migration_conn.close()


def map_sqlserver_to_postgres_type(sql_type):
    mapping = {
        'binary': 'bytea',
        'bigint': 'bigint',
        'bit': 'boolean',
        'char': 'text',
        'date': 'date',
        'datetime': 'timestamp',
        'datetime2': 'timestamp',
        'datetimeoffset': 'timestamptz',
        'decimal': 'numeric',
        'float': 'double precision',
        'image': 'bytea',
        'int': 'integer',
        'json': 'json',
        'money': 'numeric(19,4)',
        'nchar': 'text',
        'ntext': 'text',
        'numeric': 'numeric',
        'nvarchar': 'varchar',   
        'real': 'real',
        'smalldatetime': 'timestamp',
        'smallint': 'smallint',
        'smallmoney': 'numeric(10,4)',
        'text': 'text',
        'time': 'time',
        'tinyint':'smallint',
        'uniqueidentifier': 'uuid',
        'varbinary': 'bytea',
        'varchar': 'text',
        'xml': 'xml'
    }
    return mapping.get(sql_type.lower(), None)



def check_sortable_column_sql_server(data_type):
    excluded_types = {'image', 'text', 'ntext', 'sql_variant', 'xml', 'geometry', 'geography', 'hierarchyid'}
    if data_type.lower() not in excluded_types:
        return True
    else:
        return False



def create_postgres_tables_from_sqlserver(source_conn,migration_server_conn,tables):
    table_sortable_col = {}
    for table in tables:
        mirgation_server_table_name = f"{table.split('.')[0]}_{table.split('.')[-1]}"
        mirgation_server_table_name = generate_postgres_name(mirgation_server_table_name)
        source_db_schema = table.split('.')[0]
        source_db_table_name = table.split('.')[-1]
        table_present = 0
        with migration_server_conn.cursor() as cursor:
            cursor.execute(f"select count(*) FROM information_schema.tables where lower(table_type) = 'base table' and lower(table_schema) = 'public' and table_name = '{mirgation_server_table_name}'")
            result = cursor.fetchone()
            table_present = result[0]
        get_columns_query = f'''select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{source_db_table_name.replace('"', "")}' and lower(TABLE_SCHEMA) = '{source_db_schema}' '''.strip()
        columns = source_conn.execute(get_columns_query).fetchall()
        if table_present:
            print(f"Table {mirgation_server_table_name} already exists in the migration database. Skipping creation.")
            for col in columns:
                if table not in table_sortable_col.keys():
                    sortable_col = check_sortable_column_sql_server(col[1])
                    if sortable_col:
                        table_sortable_col[table] = col[0]
            continue
        else:
            print(f"Creating table {mirgation_server_table_name} in the migration database.")
            col_defs = []
            for col in columns:
                if table not in table_sortable_col.keys():
                    sortable_col = check_sortable_column_sql_server(col[1])
                    if sortable_col:
                        table_sortable_col[table] = col[0]
                postgres_datatype = map_sqlserver_to_postgres_type(col[1])
                if not postgres_datatype:
                    print(f"Unmapped source db column datatype: {col[1]}")
                    print("Add this mapping to the map_sqlserver_to_postgres_type function to proceed")
                    exit(1)
                else:
                    col_defs.append(f"{generate_postgres_name(col[0])} {postgres_datatype}")
            if col_defs and table in table_sortable_col:
                create_table_query = f"CREATE TABLE IF NOT EXISTS {mirgation_server_table_name} ({', '.join(col_defs)});"
                with migration_server_conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    migration_server_conn.commit()
                print(f"Table {mirgation_server_table_name} created successfully in the migration database.")
            else:
                print(f"Could not create table {table} because it does not have a sortable column")
    return table_sortable_col


def migrate_table_data(source_conn, migration_conn, tables, table_sortable_columns):
    for table in tables:
        mirgation_server_table_name = f"{table.split('.')[0]}_{table.split('.')[-1]}"
        mirgation_server_table_name = generate_postgres_name(mirgation_server_table_name)
        print(f"Migrating data for table {mirgation_server_table_name}")
        table_cols = None
        with migration_conn.cursor() as cursor:
            # clear the table before inserting new data
            cursor.execute(f"delete from {mirgation_server_table_name}")
        source_column_data_type_query = f'''select column_name, data_type from information_schema.columns where table_name ='{table.split('.')[-1].replace('"', "")}' and table_schema = '{table.split('.')[0]}' '''.strip()
        columns = source_conn.execute(source_column_data_type_query).fetchall()
        actual_columns = []
        # Handle column datatypes not supported by MSSQL_ODBC_DRIVER
        postgres_table_cols = []
        for column in columns:
            if column[1].lower() == "datetimeoffset":
                actual_columns.append(f'''CAST("{column[0]}" AS NVARCHAR(50)) AS {column[0]}''')
            else:
                actual_columns.append(f'"{column[0]}"')
            postgres_table_cols.append(generate_postgres_name(column[0]))
        postgres_table_cols = ",".join(postgres_table_cols).strip()
        table_cols = ",".join(actual_columns).strip()
        insert_sql = f'INSERT INTO {mirgation_server_table_name} ({postgres_table_cols}) VALUES %s'
        offset = 0
        while True:
            selection_query = f'''SELECT {table_cols} FROM {table} ORDER BY "{table_sortable_columns[table]}" OFFSET ? ROWS FETCH NEXT ? ROWS ONLY'''.strip()
            rows = source_conn.execute(
                    selection_query, 
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
        all_tables = get_source_db_tables(source_db_conn)
        if not all_tables:
            print("Source database has no tables: nothing to migrate")
            close_db_connections(source_db_conn, migration_server_conn)
            exit(1)
        else:
            print(f'Source db tables found {all_tables}')
            all_tables = set(all_tables)
        table_sortable_columns = create_postgres_tables_from_sqlserver(source_db_conn, migration_server_conn, all_tables)
        tables_to_migrate = []
        for table in all_tables:
            if table not in table_sortable_columns:
                continue
            else: 
                tables_to_migrate.append(table)
        migrate_table_data(source_db_conn, migration_server_conn, tables_to_migrate, table_sortable_columns)
        close_db_connections(source_db_conn, migration_server_conn)
    else:
        close_db_connections(source_db_conn, migration_server_conn)
        exit(1)