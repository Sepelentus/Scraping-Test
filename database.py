import os
import sqlite3

DATABASE = 'scrape_database.db'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        # Tabla de resultados de scraping
        c.execute('''
                CREATE TABLE scrape_results(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    headline TEXT,
                    subheader TEXT,
                    subsubheaders TEXT,
                    description TEXT,
                    scraping_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
        conn.close()
        print('Database created')
    else:
        print('Database already exists')

# Conexion a la base de datos
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    # Para poder acceder a los resultados por nombre de columna
    conn.row_factory = sqlite3.Row
    return conn