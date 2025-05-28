# demo-f_e-migration

Data Migration Solution

In this project there is a demo/test situation:
    The example situation is a loan lending company wants to move loan data from sql server to a their data migration server which has a postgres db.


## How to run
    1. ensure docker and python is installed on your machine
    2. clone this repositiory
    3. cd into the cloned repository directory and run docker compose up to start the containers
    4. create a virtual environment for the project python -m venv venv
    5. activate the virtual environment: -- look this up depending on os --. For linux `source  ./venv/bin/activate`
    6. install project dependencies listed in requirements.txt file with `pip install -r requirements.txt`
    7. create system environment variables to match the variables in the compose.yaml file.
    8. get the databases up and running with docker compose up
    9. connect to the 2 databases via any third party app: dbeaver || datagrip || etc
    10. run the queries present in the queries.sql file sequentially against the mssql server database

    -- This has gotten you to the starting line the next step is to then move this data to a postgres db

    11. Ensure you have microsoft odbc server for sql server installed: https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-3-proof-of-concept-connecting-to-sql-using-pyodbc?view=sql-server-ver17
    
    --

    12. Run the mssql_postgres.py: The script moves the data from sql server to postgres after
        i. Validating database connections
        ii. Fetching the tables to migrate
        iii. Creating equivalent tables on postgres after mapping the sql server column data types to postgres data types


## Future work
-[] Add partial SQL server to Postgres table migration
-[] Add the complete mapping for all sql server data types.
-[] Optimize the speed of data migration to improve performance, especially for large tables. 
-[] Add postgres to sql server migration script.
-[] Make the source and target databases parameters to the program
-[] Add constraints migration to the scripts ie: primary and foreign keys
-[] Add SQL to MongoDB script
-[] Keep design and readme files up to date
-[] Containerize the entire application
-[] Add tests to ensure changes do not break the current working implementatiton.
-[] Send std output to log files
-[] Add partial table data migration


## Contributions
