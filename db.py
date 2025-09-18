import json
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "DATABASE_URL = postgresql://bngx_o9tu_user:D8kA9EfmAiXmGze6OCqLOWaaMuA7KbBo@dpg-d35ndpbipnbc739k2lhg-a:5432/bngx_o9tu"

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def create_accounts_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            uid BIGINT UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nickname VARCHAR(255) DEFAULT ''
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

def add_account(uid, password, nickname=''):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO accounts (uid, password, nickname) VALUES (%s, %s, %s) ON CONFLICT (uid) DO NOTHING;',
                (uid, password, nickname))
    conn.commit()
    cur.close()
    conn.close()

# دالة جديدة لقراءة ملف JSON وادخال حساباته
def insert_accounts_from_json(json_file_path):
    with open(json_file_path, 'r') as f:
        accounts_list = json.load(f)

    conn = get_db_connection()
    cur = conn.cursor()
    for account in accounts_list:
        uid, password = account
        cur.execute("""
            INSERT INTO accounts (uid, password, nickname)
            VALUES (%s, %s, %s)
            ON CONFLICT (uid) DO NOTHING;
        """, (int(uid), password, ''))
    conn.commit()
    cur.close()
    conn.close()
    print(f"تم إدخال حسابات من {json_file_path} إلى قاعدة البيانات.")
