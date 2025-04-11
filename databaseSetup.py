import sqlite3
from datetime import *
import pandas as pd

def initDatebase(sqldb: str):
    
    sqliteConnection = sqlite3.connect(sqldb)
    cursor: sqlite3.Cursor = sqliteConnection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campfire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild TEXT NOT NULL,
            channel TEXT NOT NULL,
            message TEXT NOT NULL,
            endTime TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vcNotif (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild TEXT NOT NULL,
            member TEXT NOT NULL,
            sub TEXT NOT NULL,
            lastSendTime TEXT NOT NULL
        )
    ''')
    
    sqliteConnection.commit() 
    # Close the connection
    sqliteConnection.close()
    
def vcPopulate(sqldb: str, repoPath):
    sqliteConnection = sqlite3.connect(sqldb)
    cursor: sqlite3.Cursor = sqliteConnection.cursor()
    
    
    cursor.execute('SELECT * FROM vcNotif')
    
    row = cursor.fetchone()
    
    if row is None:
        df: pd.DataFrame = pd.read_csv(repoPath)
        for index, x in df.iterrows():
            cursor.execute('''
                INSERT INTO vcNotif (guild, member, sub, lastSendTime) 
                VALUES (?, ?, ?, ?)
            ''', (str(x.Guild), str(x.Member), str(x.Sub), str(datetime.min)))
            sqliteConnection.commit()
    
    # Close the connection
    sqliteConnection.close()