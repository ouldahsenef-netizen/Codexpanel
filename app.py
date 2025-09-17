from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import time
import secrets
import re
import threading
import requests
from functools import wraps
from collections import defaultdict
from db import create_accounts_table, get_all_accounts, get_account_by_id, update_account_nickname, add_account

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# إنشاء الجدول عند بدء التشغيل
create_accounts_table()

# إعدادات الحماية (كما في كودك الحالي)
S1X_PROTECTION_CONFIG = {
    'enabled': True,
    'max_attempts': 3,
    'block_duration': 15,
    'challenge_timeout': 300,
    'ddos_threshold': 10,
    'session_timeout': 1800,
    'suspicious_patterns': [
        r'bot', r'crawler', r'spider', r'scraper', r'curl', r'wget',
        r'python', r'java', r'php', r'perl', r'ruby', r'node',
        r'automated', r'script', r'tool', r'scanner', r'test'
    ]
}

verification_sessions = {}
failed_challenges = defaultdict(int)
ddos_tracker = defaultdict(lambda: defaultdict(int))
suspicious_ips = defaultdict(list)
lock = threading.Lock()

ADMIN_CREDENTIALS = {
    "bnnn": "bnnn"
}

# تابع لتحديد IP العميل
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    return request.environ.get('REMOTE_ADDR', '')

# دوال الحماية كما في كودك (is_bot_user_agent, analyze_request_pattern, وغيرها) ...

# إضافة الديكوريتر للحماية
def protection_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = get_client_ip()
        ua = request.headers.get('User-Agent', '')
        endpoint = request.path
        analysis = analyze_request_pattern(ip, endpoint, request.headers)

        if analysis == 'ddos_detected':
            return jsonify({"success": False, "error": "DDoS protection activated"}), 429
        if analysis == 'suspicious_activity' or should_challenge_request(ip, ua, endpoint):
            token = request.headers.get('X-Verification-Token')
            if token and verify_challenge_token(token, ip):
                verification_sessions[ip] = {'captcha_verified': True, 'verified_at': time.time(), 'user_agent': ua}
                return f(*args, **kwargs)
            else:
                return redirect(url_for('security_challenge'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('admin_logged_in'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('admin_login'))
    return decorated

# الراوتات الخاصة بالإدارة والهويات (مثل /admin/login, /admin/authenticate) ... كما في كودك الحالي

@app.route('/')
@protection_required
@admin_required
def index():
    accounts = get_all_accounts()
    nicknames = {str(acc['id']): acc['nickname'] for acc in accounts}
    return render_template('index.html', nicknames=nicknames)

@app.route('/api/create_account', methods=['POST'])
@protection_required
@admin_required
def create_account():
    data = request.json or {}
    account_id = data.get('account_id')
    nickname = data.get('nickname')
    if not account_id or not nickname:
        return jsonify({"success": False, "message": "يجب تحديد الحساب والاسم الجديد"}), 400

    account = get_account_by_id(account_id)
    if not account:
        return jsonify({"success": False, "message": "الحساب المختار غير صحيح"}), 400

    uid = account['uid']
    password = account['password']

    try:
        oauth_url = f"https://jwt-silk-xi.vercel.app/api/oauth_guest?uid={uid}&password={password}"
        oauth_response = requests.get(oauth_url, timeout=5)
        oauth_response.raise_for_status()
        oauth_data = oauth_response.json()
        token = oauth_data.get('token')

        if not token:
            return jsonify({"success": False, "message": "فشل في الحصول على التوكن من API"}), 500

        change_nick_url = f"https://change-name-gray.vercel.app/lvl_up/api/nickname?jwt_token={token}&nickname={nickname}"
        nick_response = requests.get(change_nick_url, timeout=5)
        nick_response.raise_for_status()
        nick_data = nick_response.json()

        if nick_data.get('success', False):
            update_account_nickname(account_id, nickname)
            return jsonify({"success": True, "message": "تم تغيير الاسم بنجاح"}), 200
        else:
            error_msg = nick_data.get('message', "فشل في تغيير الاسم")
            return jsonify({"success": False, "message": error_msg}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ داخلي: {str(e)}"}), 500

@app.route('/api/add_friend', methods=['POST'])
@protection_required
@admin_required
def add_friend():
    data = request.json or {}
    account_id = data.get('account_id')
    friend_uid = data.get('friend_uid')
    days = data.get('days', None)  # القيمة الجديدة

    if not account_id or not friend_uid:
        return jsonify({"success": False, "message": "يجب تحديد الحساب والـ UID لإضافة الصديق"}), 400

    account = accounts.get(account_id)
    if not account:
        return jsonify({"success": False, "message": "الحساب المختار غير صحيح"}), 400

    uid = account['uid']
    password = account['password']

    try:
        oauth_url = f"https://jwt-silk-xi.vercel.app/api/oauth_guest?uid={uid}&password={password}"
        oauth_response = requests.get(oauth_url, timeout=5)
        oauth_response.raise_for_status()
        oauth_data = oauth_response.json()
        token = oauth_data.get('token')
        if not token:
            return jsonify({"success": False, "message": "فشل في الحصول على التوكن"}), 500

        add_url = ADD_URL_TEMPLATE.format(token=token, uid=friend_uid)
        add_response = requests.get(add_url, timeout=5)
        add_response.raise_for_status()
        add_data = add_response.json()

        if add_data.get('success', False):
            # إذا كانت قيمة الأيام موجودة، نرسل طلب إضافي لل API الخارجي
            if days is not None:
                try:
                    api_url = f"https://time-bngx-0c2h.onrender.com/api/add_uid?uid={friend_uid}&time={days}&type=days&permanent=false"
                    external_resp = requests.get(api_url, timeout=5)
                    external_resp.raise_for_status()
                    external_data = external_resp.json()
                    if external_data.get('success') or external_data.get('message'):
                        return jsonify({"success": True, "message": "تمت إضافة الصديق بنجاح وتم إرسال عدد الأيام بنجاح."})
                    else:
                        return jsonify({"success": True, "message": "تمت إضافة الصديق بنجاح ولكن حدث خطأ في إرسال عدد الأيام."})
                except Exception as e:
                    return jsonify({"success": True, "message": f"تمت إضافة الصديق بنجاح لكن حدث خطأ أثناء إرسال عدد الأيام: {str(e)}"})
            else:
                return jsonify({"success": True, "message": "تمت إضافة الصديق بنجاح"})
        else:
            error_msg = add_data.get('message', "فشل في إضافة الصديق")
            return jsonify({"success": False, "message": error_msg})
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ داخلي: {str(e)}"}), 500

@app.route('/api/remove_friend', methods=['POST'])
@protection_required
@admin_required
def remove_friend():
    data = request.json or {}
    account_id = data.get('account_id')
    friend_uid = data.get('friend_uid')

    if not account_id or not friend_uid:
        return jsonify({"success": False, "message": "يجب تحديد الحساب والـ UID للصديق"}), 400

    account = accounts.get(account_id)
    if not account:
        return jsonify({"success": False, "message": "الحساب المختار غير صحيح"}), 400

    uid = account['uid']
    password = account['password']

    try:
        oauth_url = f"https://jwt-silk-xi.vercel.app/api/oauth_guest?uid={uid}&password={password}"
        oauth_response = requests.get(oauth_url, timeout=5)
        oauth_response.raise_for_status()
        oauth_data = oauth_response.json()
        token = oauth_data.get('token')
        if not token:
            return jsonify({"success": False, "message": "فشل في الحصول على التوكن"}), 500

        remove_url = REMOVE_URL_TEMPLATE.format(token=token, uid=friend_uid)
        remove_response = requests.get(remove_url, timeout=5)
        remove_response.raise_for_status()
        remove_data = remove_response.json()

        if remove_data.get('success', False):
            return jsonify({"success": True, "message": "تم إزالة الصديق بنجاح"})
        else:
            error_msg = remove_data.get('message', "فشل في إزالة الصديق")
            return jsonify({"success": False, "message": error_msg})
    except Exception as e:
        return jsonify({"success": False, "message": f"خطأ داخلي: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
