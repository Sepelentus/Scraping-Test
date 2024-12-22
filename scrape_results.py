import sqlite3

DATABASE = 'scrape_database.db'

def view_db_contents():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM scrape_results')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == '__main__':
    view_db_contents()