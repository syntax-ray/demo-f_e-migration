# demo-f_e-migration

This is a demo project to set up and test data migration from sql server to postgres to a third party system.

In this demo project:
    The example situation is a loan lending company wants to move loan data from sql server to the third party system.


# How to run
    1. Ensure docker and python is installed on your machine
    2. Clone this repositiory
    3. cd into the cloned repository directory and run docker compose up to start the containers
    4. create a virtual environment for the project python -m venv venv
    5. activate the virtual environment: -- look this up depending on os --. For linux (source  ./venv/bin/activate)
    6. install project dependencies listed in requirements.txt file with