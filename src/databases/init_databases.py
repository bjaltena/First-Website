import sqlite3

from config.secrets import ADMIN_PASSWORD, PERSONAL_EMAIL, TEST_USER_PASSWORD
from passlib.hash import sha256_crypt

posts_connection = sqlite3.connect("src/databases/posts.db")

with open("src/databases/posts_schema.sql") as f:
    posts_connection.executescript(f.read())

cur = posts_connection.cursor()
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ("First Post", "Content for the first post"))
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", ("Second Post", "Content for the second post"))
posts_connection.commit()
posts_connection.close()


users_connection = sqlite3.connect("src/databases/users.db")

with open("src/databases/users_schema.sql") as f:
    users_connection.executescript(f.read())

cur = users_connection.cursor()
cur.execute(
    "INSERT INTO users (username, password, email, permission) " "VALUES (?, ?, ?, ?)",
    ("admin", sha256_crypt.hash(secret=ADMIN_PASSWORD), PERSONAL_EMAIL, "Admin"),
)
cur.execute(
    "INSERT INTO users (username, password, email) " "VALUES (?, ?, ?)",
    ("testUser", sha256_crypt.hash(secret=TEST_USER_PASSWORD), PERSONAL_EMAIL),
)

users_connection.commit()
users_connection.close()
