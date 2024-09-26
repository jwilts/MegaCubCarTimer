# db_connection.py

import mysql.connector
import RMSettings  

def get_db_connection():
    db = mysql.connector.connect(
        host=RMSettings.host,
        user=RMSettings.user,
        passwd=RMSettings.passwd,
        database=RMSettings.database
    )
    return db

def get_cursor(db):
    return db.cursor(buffered=True)