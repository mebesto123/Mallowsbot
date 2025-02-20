import sqlite3

def initDatebase(sqldb: str):
    
    sqliteConnection = sqlite3.connect(sqldb)
    cursor: sqlite3.Cursor = sqliteConnection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camfire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild TEXT NOT NULL,
            channel TEXT NOT NULL,
            message TEXT NOT NULL,
            endTime TEXT NOT NULL
        )
    ''')
    
    sqliteConnection.commit() 
    # Close the connection
    sqliteConnection.close()