# demo-f_e-migration

This is a demo project to set up and test data migration from sql server to postgres to a third party system.

In this demo project:
    The example situation is a loan lending company wants to move loan data from sql server to the third party system.


# How to run
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
        ii.