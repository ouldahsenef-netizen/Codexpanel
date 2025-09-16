from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import requests
import time
import secrets
import hashlib
import hmac
import base64
import json
from functools import wraps
from collections import defaultdict
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # ضروري للجلسات

# -------- حسابات البوت --------
accounts = {
    "1": {"uid": 4168796933, "password": "FOX_FOX_BY8VI2JJ", "nickname": ""},
    "2": {"uid": 4168796929, "password": "FOX_FOX_YMPSFPKD", "nickname": ""},
    "3": {"uid": 4168796924, "password": "FOX_FOX_9WASGXSJ", "nickname": ""},
}

ADD_URL_TEMPLATE = "https://add-friend-weld.vercel.app/add_friend?token={token}&uid={uid}"
REMOVE_URL_TEMPLATE = "https://remove-self.vercel.app/remove_friend?token={token}&uid={uid}"

# -------- حماية S1X TEAM --------
S1X_PROTECTION_CONFIG = {
    'enabled': True,
    'max_attempts': 3,
    'block_duration': 15,
    'challenge_timeout': 300,
    'suspicious_patterns': [
        r'bot', r'crawler', r'spider', r'scraper', r'curl', r'wget',
        r'python', r'java', r'php', r'perl', r'ruby', r'node',
        r'automated', r'script', r'tool', r'scanner', r'test'
    ]
}

verification_sessions = {}
failed_challenges = defaultdict(int)

# جدول المستخدمين الإداريين (للدخول)
ADMIN_USERS = {
    "admin": {
        "password": "adminpass",  # غيّرها لكلمة سر آمنة
    }
}

def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ.get('REMOTE_ADDR', '')
    else:
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()

def is_bot_user_agent(user_agent):
    if not user_agent:
        return True
    ua = user_agent.lower()
    for pattern in S1X_PROTECTION_CONFIG['suspicious_patterns']:
        if re.search(pattern, ua):
            return True
    known_browsers = ['mozilla', 'webkit', 'chrome', 'firefox', 'safari', 'edge']
    return not any(browser in ua for browser in known_browsers)

# ديكوريتر للحماية والتأكد من الكابتشا ثم الدخول
def codex_protection_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = get_client_ip()
        ua = request.headers.get('User-Agent', '')
        endpoint = request.path

        session_data = verification_sessions.get(ip)
        if session_data and session_data.get('captcha_verified', False) and session_data.get('admin_logged_in', False):
            if time.time() - session_data.get('verified_at', 0) < 1800:
                return f(*args, **kwargs)
            else:
                # انتهاء صلاحية الجلسة
                verification_sessions.pop(ip, None)

        # إذا لم يدخل المستخدم التحقق أو لم يسجل دخول، نوجهه لكابتشا أو تسجيل دخول
        if not session_data or not session_data.get('captcha_verified', False):
            if request.is_json or '/api/' in endpoint:
                return jsonify({
                    'success': False,
                    'error': 'Security challenge required',
                    'message': 'Please complete security verification',
                    'challenge_url': url_for('security_challenge'),
                    'code': 403
                }), 403
            else:
                return redirect(url_for('security_challenge'))

        if not session_data.get('admin_logged_in', False):
            return redirect(url_for('admin_login'))

        return f(*args, **kwargs)
    return decorated

@app.route('/api/security/generate-challenge')
def generate_challenge():
    import random
    operations = ['+', '-', '*']
    op = random.choice(operations)
    if op == '+':
        n1 = random.randint(1, 50)
        n2 = random.randint(1, 50)
        answer = n1 + n2
    elif op == '-':
        n1 = random.randint(20, 70)
        n2 = random.randint(1, 20)
        answer = n1 - n2
    else:
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        answer = n1 * n2
    question = f"{n1} {op} {n2} = ?"
    session['captcha_answer'] = answer
    return jsonify({"question": question})

@app.route('/security/challenge')
def security_challenge():
    return render_template('captcha.html')

@app.route('/api/security/verify-human', methods=['POST'])
def verify_human():
    client_ip = get_client_ip()
    data = request.json
    user_answer = data.get('answer')
    user_agent = data.get('user_agent', '')

    if not user_answer or session.get('captcha_answer') is None:
        return jsonify({"success": False, "message": "Invalid challenge data"}), 400

    try:
        user_answer = int(user_answer)
    except ValueError:
        return jsonify({"success": False, "message": "Answer must be a number"}), 400

    correct_answer = session.get('captcha_answer')

    if user_answer == correct_answer:
        verification_sessions[client_ip] = {
            'captcha_verified': True,
            'verified_at': time.time(),
            'user_agent': user_agent,
            'admin_logged_in': False  # للدخول بعدها إلى صفحة تسجيل الدخول
        }
        failed_challenges.pop(client_ip, None)
        return jsonify({"success": True, "message": "Verification successful"})
    else:
        failed_challenges[client_ip] += 1
        if failed_challenges[client_ip] >= S1X_PROTECTION_CONFIG['max_attempts']:
            return jsonify({"success": False, "message": "Exceeded max attempts. IP temporarily blocked."}), 403
        return jsonify({"success": False, "message": "Incorrect answer. Try again."}), 403

@app.route('/admin/login', methods=['GET'])
def admin_login():
    # تعرض صفحة تسجيل الدخول فقط بعد نجاح الكابتشا
    ip = get_client_ip()
    session_data = verification_sessions.get(ip)
    if not session_data or not session_data.get('captcha_verified', False):
        return redirect(url_for('security_challenge'))
    return render_template('admin_login.html')

@app.route('/admin/authenticate', methods=['POST'])
def admin_authenticate():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    ip = get_client_ip()
    session_data = verification_sessions.get(ip)

    if not session_data or not session_data.get('captcha_verified', False):
        return jsonify({'success': False, 'message': 'Complete CAPTCHA verification first.'}), 403

    user = ADMIN_USERS.get(username)
    if user and user['password'] == password:
        verification_sessions[ip]['admin_logged_in'] = True
        verification_sessions[ip]['verified_at'] = time.time()
        session_id = secrets.token_hex(16)
        verification_sessions[ip]['session_id'] = session_id
        return jsonify({'success': True, 'session_id': session_id})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password.'})

@app.route('/')
@codex_protection_required
def index():
    nicknames = {k: v['nickname'] for k, v in accounts.items()}
    return render_template('index.html', nicknames=nicknames)

# تبقى باقي الدوال API كما هي مع ديكوريتر الحماية

# ... (الدوال create_acc, add_friend, remove_friend من الكود السابق تبقى كما هي مع @codex_protection_required)

if __name__ == '__main__':
    app.run(debug=True)
