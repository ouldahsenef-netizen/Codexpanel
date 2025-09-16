import os
import json
import secrets
import re
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, \
    logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'bbngx_login'

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    max_accounts = db.Column(db.Integer, default=3)

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

ACCOUNTS_FILE = 'accs.json'
OWNERSHIP_FILE = 'user_bot_owners.json'

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {str(acc['uid']): acc for acc in data}
    return {}

def load_user_bot_owners():
    if os.path.exists(OWNERSHIP_FILE):
        with open(OWNERSHIP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_bot_owners(data):
    with open(OWNERSHIP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

accounts = load_accounts()
user_bot_owners = load_user_bot_owners()

S1X_PROTECTION_CONFIG = {
    'max_attempts': 3,
    'challenge_timeout': 300,
    'suspicious_patterns': [
        r'bot', r'crawler', r'spider', r'scraper', r'curl', r'wget',
        r'python', r'java', r'php', r'perl', r'ruby', r'node',
        r'automated', r'script', r'tool', r'scanner', r'test'
    ]
}

def is_bot_user_agent(user_agent):
    if not user_agent:
        return True
    ua = user_agent.lower()
    for pattern in S1X_PROTECTION_CONFIG['suspicious_patterns']:
        if re.search(pattern, ua):
            return True
    known = ['mozilla', 'webkit', 'chrome', 'firefox', 'safari', 'edge']
    return not any(k in ua for k in known)

def generate_challenge():
    import random
    ops = ['+', '-', '*']
    op = random.choice(ops)
    if op == '+':
        n1 = random.randint(1, 50)
        n2 = random.randint(1, 50)
        ans = n1 + n2
    elif op == '-':
        n1 = random.randint(20, 70)
        n2 = random.randint(1, 20)
        ans = n1 - n2
    else:
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        ans = n1 * n2
    return f"{n1} {op} {n2} = ?", ans

@app.route('/api/security/generate-challenge')
def api_generate_challenge():
    q, a = generate_challenge()
    session['captcha_answer'] = a
    return jsonify({'question': q})

@app.route('/security/challenge')
def security_challenge():
    return render_template('captcha.html')

@app.route('/api/security/verify-human', methods=['POST'])
def verify_human():
    answer = request.json.get('answer')
    try:
        answer = int(answer)
    except:
        return jsonify({"success": False, "message": "الرجاء إدخال عدد صحيح"}), 400
    correct = session.get('captcha_answer')
    if correct is None:
        return jsonify({"success": False, "message": "الرجاء توليد التحدي أولاً"}), 400
    if answer == correct:
        session['captcha_verified'] = True
        return jsonify({"success": True, "message": "تم التحقق بنجاح"})
    else:
        return jsonify({"success": False, "message": "الإجابة خاطئة"}), 403

@app.route('/bbngx_login', methods=['GET', 'POST'])
def bbngx_login():
    if not session.get('captcha_verified'):
        return redirect(url_for('security_challenge'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            session['captcha_verified'] = True
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور خاطئة', 'error')
            return redirect(url_for('bbngx_login'))
    return render_template('bbngx_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    session.pop('captcha_verified', None)
    session.pop('username', None)
    flash('تم تسجيل الخروج', 'success')
    return redirect(url_for('bbngx_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    username = current_user.username
    max_accounts = current_user.max_accounts
    owned_uids = user_bot_owners.get(username, [])
    owned_accounts = [accounts[uid] for uid in owned_uids if uid in accounts]
    return render_template('dashboard.html',
                           bots=owned_accounts,
                           max_accounts=max_accounts,
                           current_count=len(owned_accounts),
                           user=username)

@app.route('/admin/add_bot', methods=['POST'])
@login_required
def add_bot():
    username = current_user.username
    uid = request.form.get('uid')
    if uid not in accounts:
        flash('الحساب غير موجود في accs.json')
        return redirect(url_for('admin_dashboard'))
    owned_uids = user_bot_owners.get(username, [])
    if len(owned_uids) >= current_user.max_accounts:
        flash('وصلت للحد الأقصى لحسابات البوت')
        return redirect(url_for('admin_dashboard'))
    if uid in owned_uids:
        flash('هذا الحساب مملوك لك مسبقاً')
        return redirect(url_for('admin_dashboard'))
    owned_uids.append(uid)
    user_bot_owners[username] = owned_uids
    save_user_bot_owners(user_bot_owners)
    flash('تم إضافة الحساب بنجاح')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_bot', methods=['POST'])
@login_required
def delete_bot():
    username = current_user.username
    uid = request.form.get('uid')
    owned_uids = user_bot_owners.get(username, [])
    if uid in owned_uids:
        owned_uids.remove(uid)
        user_bot_owners[username] = owned_uids
        save_user_bot_owners(user_bot_owners)
        flash('تم حذف الحساب بنجاح')
    else:
        flash('الحساب غير مملوك لك')
    return redirect(url_for('admin_dashboard'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# البديل لـ before_first_request لتشغيل الكود مرة واحدة فقط
def initial_setup():
    db.create_all()
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='admin', password='adminpass', max_accounts=5)
        db.session.add(admin)
        db.session.commit()

def run_once():
    if not hasattr(app, 'initial_setup_done'):
        initial_setup()
        app.initial_setup_done = True

@app.before_request
def before_request_func():
    run_once()

if __name__ == '__main__':
    app.run(debug=True)
