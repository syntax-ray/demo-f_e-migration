# Data Migration Solution

In this project there is a demo/test situation:
    The example situation is a loan lending company wants to move loan data from sql server to a their data migration server which has a postgres db.


## How to run
    1. ensure docker and python is installed on your machine
    2. clone this repositiory
    3. cd into the cloned repository directory and run `docker compose up` to start the containers
    4. create a virtual environment for the project `python -m venv venv`
    5. activate the virtual environment: -- look this up depending on os --. For linux `source  ./venv/bin/activate`
    6. install project dependencies listed in requirements.txt file with `pip install -r requirements.txt`
    7. create system environment variables to match the variables in the compose.yaml file.
    8. get the databases up and running with `docker compose up` or my preferred `docker compose up -d` to 
         free up the terminal for REPL.
    9. connect to the 2 databases via any third party app: dbeaver || datagrip || etc
    10. run the queries present in the queries.sql file sequentially against the mssql server database to create the demo/test
         situation tables and insert the dummy data.
    11. Ensure you have microsoft odbc server for sql server installed: https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-3-proof-of-concept-connecting-to-sql-using-pyodbc?view=sql-server-ver17. Update the global variable MSSQL_ODBC_DRIVER
        located in mssql_postgres.py with the installed odbc version.
    12. Run the mssql_postgres.py: The script moves the data from sql server to postgres after
        i. Validating database connections
        ii. Fetching the tables to migrate
        iii. Creating non existing equivalent tables on postgres after mapping the sql server column datatypes to postgres datatypes
        iv. Migrating the table data from sql server to postgres in batches


## Future work
- [x] Add partial SQL server to Postgres table migration
- [x] Add the complete SQL server to Postgres mapping.
- [x] Support SQL server tables and columns with non conventional names Eg: table names with spaces
- [] Optimize the speed of data migration to improve performance, especially for large tables. 
- [] Add postgres to sql server migration script.
- [] Make the source and target databases parameters to the program
- [] Add constraints migration to the scripts ie: primary and foreign keys
- [] Add SQL to MongoDB script
- [] Keep design and readme files up to date
- [] Containerize the entire application
- [] Add tests to ensure changes do not break the current working implementatiton.
- [] Send std output to log files
- [] Add partial table data migration


## Contributions
