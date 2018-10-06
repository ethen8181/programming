"""https://docs.python.org/3.6/library/sqlite3.html"""
import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# INTEGER PRIMARY KEY serves as the autoincrement column in sqlite
create_users_table_statement = """
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)
"""
cursor.execute(create_users_table_statement)

create_items_table_statement = """
    CREATE TABLE IF NOT EXISTS items(name TEXT, price REAL)
"""
cursor.execute(create_items_table_statement)

connection.commit()
connection.close()
