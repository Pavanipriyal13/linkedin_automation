import sqlite3

DB_PATH = "job_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            company TEXT,
            is_applied INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def insert_job(title, link, company):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO jobs (title, link, company) VALUES (?, ?, ?)', (title, link, company))
    conn.commit()
    conn.close()

def get_pending_jobs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, link, company FROM jobs WHERE is_applied = 0')
    jobs = c.fetchall()
    conn.close()
    return jobs

def mark_job_as_applied(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE jobs SET is_applied = 1 WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()
