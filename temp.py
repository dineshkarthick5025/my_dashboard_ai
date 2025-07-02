import psycopg2
from psycopg2 import sql

# Connection details for the existing 'ai_analytics' database (any existing DB works to connect)
host = "95.177.179.236"
port = 5400
user = "postgres"
password = "DbT!4485$"

# Name of the new database you want to create
new_db_name = "my_dashboard"

# Connect to the server (connect to default 'postgres' DB)
try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="ai_analytics"  # We connect to 'postgres' or any existing DB to run CREATE DATABASE
    )
    connection.autocommit = True  # Required for CREATE DATABASE

    with connection.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db_name)))
        print(f"Database '{new_db_name}' created successfully.")

except Exception as e:
    print(f"Error creating database: {e}")

finally:
    if connection:
        connection.close()
