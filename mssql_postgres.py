import os


source_db = {
    "host": os.getenv("DEMO_SOURCE_HOST", 'localhost'),
    "port": os.getenv("DEMO_SOURCE_PORT"),
    "user": os.getenv("DEMO_SOURCE_USER"),
    "password": os.getenv("DEMO_SOURCE_PASSWORD")
}    




if __name__ == "__main__":
    print(source_db)