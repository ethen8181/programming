"""https://docs.python.org/3.6/library/sqlite3.html"""
import sqlite3


connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table_statement = """
    CREATE TABLE IF NOT EXISTS users(id INT, username TEXT, password TEXT)
"""
cursor.execute(create_table_statement)

insert_user_statement = "INSERT INTO users VALUES(?, ?, ?)"

# inserting one record
user = (1, 'ethen', 'asdf')
cursor.execute(insert_user_statement, user)

# inserting multiple records
users = [
    (2, 'rolf', 'asdf'),
    (3, 'anne', 'xyz')
]
cursor.executemany(insert_user_statement, users)

# looping through the result of a SELECT statement as an iterator
print("get all users in database:")
get_all_users_statement = "SELECT * FROM users"
for row in cursor.execute(get_all_users_statement):
    print(row)
    
# fetch the first result
print("\nget first user in database:")
result = cursor.execute(get_all_users_statement)
row = result.fetchone()
print(row)

connection.commit()
connection.close()