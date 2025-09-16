import os
import secrets
from flask import Flask, request, redirect, url_for, flash, session, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# المتغير لتشغيل الإعداد أول مرة فقط
setup_done = False

# النماذج

class SuperAdmin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    max_accounts = db.Column(db.Integer, default=3)

class BotAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    user1 = SuperAdmin.query.get(int(user_id))
    if user1:
        user1.is_superadmin = True
        return user1
    user2 = AdminUser.query.get(int(user_id))
    if user2:
        user2.is_superadmin = False
        return user2
    return None

# Captcha
import random

def generate_captcha():
    ops = ['+', '-', '*']
    op = random.choice(ops)
    if op == '+':
        n1 = random.randint(1, 30)
        n2 = random.randint(1, 30)
        ans = n1 + n2
    elif op == '-':
        n1 = random.randint(20, 50)
        n2 = random.randint(1, 20)
        ans = n1 - n2
    else:
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        ans = n1 * n2
    q = f"{n1} {op} {n2} = ?"
    return q, ans

@app.route('/captcha')
def captcha():
    question, answer = generate_captcha()
    session['captcha_answer'] = answer
    return render_template('captcha.html', question=question)

@app.route('/captcha/verify', methods=['POST'])
def captcha_verify():
    answer = request.form.get('answer')
    try:
        answer = int(answer)
    except:
        flash('يرجى إدخال رقم صحيح')
        return redirect(url_for('captcha'))
    if answer == session.get('captcha_answer'):
        session['captcha_verified'] = True
        return redirect(url_for('superadmin_login'))
    else:
        flash('الإجابة خاطئة، حاول مرة أخرى')
        return redirect(url_for('captcha'))

# سبل التشغيل أول مرة
@app.before_request
def before_request():
    global setup_done
    if not setup_done:
        db.create_all()
        # اضافة سوبر ادمين افتراضي
        if not SuperAdmin.query.filter_by(username='superadmin').first():
            sa = SuperAdmin(username='superadmin', password='superpass')
            db.session.add(sa)
            db.session.commit()
        setup_done = True

# تسجيل دخول السوبر أدمين
@app.route('/superadmin/login', methods=['GET','POST'])
def superadmin_login():
    if not session.get('captcha_verified'):
        return redirect(url_for('captcha'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = SuperAdmin.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('superadmin_panel'))
        flash('اسم المستخدم أو كلمة المرور خاطئة')
    return render_template('superadmin_login.html')

# لوحة تحكم السوبر أدمين
@app.route('/superadmin/panel')
@login_required
def superadmin_panel():
    if not getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('admin_login'))
    admins = AdminUser.query.all()
    return render_template('superadmin_panel.html', admins=admins)

# انشاء أعضاء أدمين جدد
@app.route('/superadmin/create_admin', methods=['POST'])
@login_required
def create_admin():
    if not getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('admin_login'))
    username = request.form.get('username')
    password = request.form.get('password')
    max_accounts = int(request.form.get('max_accounts'))
    if AdminUser.query.filter_by(username=username).first():
        flash('اسم المستخدم موجود مسبقاً')
        return redirect(url_for('superadmin_panel'))
    new_admin = AdminUser(username=username, password=password, max_accounts=max_accounts)
    db.session.add(new_admin)
    db.session.commit()
    flash('تم إنشاء حساب إداري جديد')
    return redirect(url_for('superadmin_panel'))

# تسجيل دخول الأعضاء العاديين
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if not session.get('captcha_verified'):
        return redirect(url_for('captcha'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('اسم المستخدم أو كلمة المرور خاطئة')
    return render_template('admin_login.html')

# لوحة تحكم الأدمين لإدارة البوتات
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('superadmin_panel'))
    bots = BotAccount.query.filter_by(owner_id=current_user.id).all()
    return render_template('admin_dashboard.html', bots=bots, max_accounts=current_user.max_accounts)

# اضافة بوت جديد
@app.route('/admin/add_bot', methods=['POST'])
@login_required
def add_bot():
    if getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('superadmin_panel'))
    uid = request.form.get('uid')
    password = request.form.get('password')

    if BotAccount.query.filter_by(uid=uid).first():
        flash('هذا الحساب موجود مسبقاً')
        return redirect(url_for('admin_dashboard'))

    count = BotAccount.query.filter_by(owner_id=current_user.id).count()
    if count >= current_user.max_accounts:
        flash('وصلت الحد الأقصى لحسابات البوت')
        return redirect(url_for('admin_dashboard'))

    new_bot = BotAccount(uid=uid, password=password, owner_id=current_user.id)
    db.session.add(new_bot)
    db.session.commit()
    flash('تم إضافة حساب بوت جديد')
    return redirect(url_for('admin_dashboard'))

# حذف بوت
@app.route('/admin/delete_bot/<int:bot_id>', methods=['POST'])
@login_required
def delete_bot(bot_id):
    bot = BotAccount.query.get(bot_id)
    if bot and bot.owner_id == current_user.id:
        db.session.delete(bot)
        db.session.commit()
        flash('تم حذف حساب بوت')
    else:
        flash('ليس لديك صلاحية لحذف هذا الحساب')
    return redirect(url_for('admin_dashboard'))

# تسجيل خروج
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('captcha_verified', None)
    flash('تم تسجيل الخروج')
    return redirect(url_for('admin_login'))

# ========== القوالب ==========

captcha_html = """
<!doctype html>
<html lang='ar' dir='rtl'>
<head>
<meta charset='utf-8' />
<title>CAPTCHA</title>
</head>
<body style='background:black; color:#0f0; font-family: monospace; text-align:center; padding:20px;'>
<h1>حل اختبار التحقق</h1>
<form method='POST' action='/captcha/verify'>
<p style='font-size:20px;'>{{ question }}</p>
<input name='answer' type='number' required style='font-size: 18px; padding:5px;'/>
<button type='submit' style='font-size:18px; margin-top:10px;'>تحقق</button>
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <p style='color:red;'>{{ messages[0] }}</p>
  {% endif %}
{% endwith %}
</body>
</html>
"""

superadmin_login_html = """
<!doctype html>
<html lang='ar' dir='rtl'>
<head><meta charset='utf-8' /><title>دخول السوبر أدمن</title></head>
<body style='background:#000;color:#0f0;font-family:monospace;text-align:center;'>
<h1>تسجيل دخول السوبر أدمن</h1>
<form method='POST'>
<input name='username' placeholder='اسم المستخدم' required />
<input name='password' type='password' placeholder='كلمة المرور' required />
<button type='submit'>دخول</button>
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <p style='color:red;'>{{ messages[0] }}</p>
  {% endif %}
{% endwith %}
</body>
</html>
"""

superadmin_panel_html = """
<!doctype html>
<html lang='ar' dir='rtl'>
<head><meta charset='utf-8' /><title>لوحة السوبر أدمن</title></head>
<body style='background:#000;color:#0f0;font-family:monospace;padding:20px;'>
<h1>لوحة تحكم السوبر أدمن</h1>
<p><a href='/logout' style='color:#f00;'>تسجيل خروج</a></p>
<h2>إنشاء حساب إداري جديد</h2>
<form method='POST' action='/superadmin/create_admin'>
<input name='username' placeholder='اسم المستخدم' required />
<input name='password' type='password' placeholder='كلمة المرور' required />
<input name='max_accounts' type='number' min='1' value='3' required />
<button type='submit'>إنشاء</button>
</form>
<h2>قائمة الأعضاء الإداريين</h2>
<table border='1' cellpadding='5' style='width:100%;color:#0f0;'>
<tr><th>اسم المستخدم</th><th>الحد الأقصى لحسابات البوت</th></tr>
{% for admin in admins %}
<tr><td>{{ admin.username }}</td><td>{{ admin.max_accounts }}</td></tr>
{% else %}
<tr><td colspan='2'>لا يوجد أعضاء.</td></tr>
{% endfor %}
</table>
</body>
</html>
"""

admin_login_html = """
<!doctype html>
<html lang='ar' dir='rtl'>
<head><meta charset='utf-8' /><title>دخول الأدمن</title></head>
<body style='background:#000;color:#0f0;font-family:monospace;text-align:center;'>
<h1>تسجيل دخول الأدمن</h1>
<form method='POST'>
<input name='username' placeholder='اسم المستخدم' required />
<input name='password' type='password' placeholder='كلمة المرور' required />
<button type='submit'>دخول</button>
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <p style='color:red;'>{{ messages[0] }}</p>
  {% endif %}
{% endwith %}
</body>
</html>
"""

admin_dashboard_html = """
<!doctype html>
<html lang='ar' dir='rtl'>
<head><meta charset='utf-8' /><title>لوحة تحكم الأدمن</title></head>
<body style='background:#000;color:#0f0;font-family:monospace;padding:20px;'>
<h1>لوحة تحكم الأدمن</h1>
<p>مرحباً، {{ current_user.username }} | <a href='/logout' style='color:#f00;'>تسجيل خروج</a></p>
<h2>حسابات البوت المخصصة لك (الحد الأقصى: {{ max_accounts }})</h2>
<table border='1' cellpadding='5' style='width:100%;color:#0f0;'>
<thead>
<tr><th>UID</th><th>كلمة المرور</th><th>حذف</th></tr>
</thead>
<tbody>
{% for bot in bots %}
<tr>
<td>{{ bot.uid }}</td>
<td>{{ bot.password }}</td>
<td>
<form method='POST' action='/admin/delete_bot/{{ bot.id }}'>
<button type='submit'>حذف</button>
</form>
</td>
</tr>
{% else %}
<tr><td colspan='3'>لا يوجد حسابات بوت في الوقت الحالي</td></tr>
{% endfor %}
</tbody>
</table>
<h3>إضافة حساب بوت جديد</h3>
<form method='POST' action='/admin/add_bot'>
<label>UID:</label><input name='uid' required />
<label>كلمة المرور:</label><input name='password' required />
<button type='submit'>إضافة</button>
</form>
</body>
</html>
"""

@app.route('/captcha.html')
def captcha_html():
    question, answer = generate_captcha()
    session['captcha_answer'] = answer
    return render_template_string(captcha_html, question=question)

@app.route('/superadmin_login.html')
def superadmin_login_html_page():
    return render_template_string(superadmin_login_html)

@app.route('/superadmin_panel.html')
def superadmin_panel_html_page():
    admins = AdminUser.query.all()
    return render_template_string(superadmin_panel_html, admins=admins)

@app.route('/admin_login.html')
def admin_login_html_page():
    return render_template_string(admin_login_html)

@app.route('/admin_dashboard.html')
def admin_dashboard_html_page():
    bots = BotAccount.query.filter_by(owner_id=current_user.id).all()
    return render_template_string(admin_dashboard_html, bots=bots, max_accounts=current_user.max_accounts)

# بدء التشغيل
if __name__ == '__main__':
    app.run(debug=True)
