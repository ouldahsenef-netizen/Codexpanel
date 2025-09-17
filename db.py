import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        database="bngx",
        user="bngx_user",
        password="XqYueLZSWajZCbBLHZ6WkOpJxFKZi0bZ",
        host="dpg-d34rj956ubrc73cm6mu0-a",
        port="5432"
    )
    return conn

def create_accounts_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            uid BIGINT UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nickname VARCHAR(255)
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def get_all_accounts():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM accounts;')
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return accounts

def get_account_by_id(account_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM accounts WHERE id = %s;', (account_id,))
    account = cur.fetchone()
    cur.close()
    conn.close()
    return account

def update_account_nickname(account_id, nickname):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE accounts SET nickname=%s WHERE id=%s;', (nickname, account_id))
    conn.commit()
    cur.close()
    conn.close()

def add_account(uid, password, nickname):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO accounts (uid, password, nickname) VALUES (%s, %s, %s);',
                (uid, password, nickname))
    conn.commit()
    cur.close()
    conn.close()
