import os
import json
import secrets
import re
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'bbngx_login'

# ===== MODELS =====

class SuperAdmin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    max_accounts = db.Column(db.Integer, default=3)

class BotAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'))

@login_manager.user_loader
def load_user(user_id):
    user = SuperAdmin.query.get(int(user_id))
    if user:
        user.is_superadmin = True
        return user
    user = AdminUser.query.get(int(user_id))
    if user:
        user.is_superadmin = False
        return user
    return None

# ===== CAPTCHA protection (simplified) =====

def generate_captcha():
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

@app.route('/security/challenge')
def security_challenge():
    question, answer = generate_captcha()
    session['captcha_answer'] = answer
    return render_template_string('''
    <html><head><title>CAPTCHA</title></head><body style="background:#000;color:#0f0;font-family:monospace;text-align:center;">
    <h1>حل CAPTCHA للتحقق</h1>
    <form method="POST" action="{{ url_for('verify_captcha') }}">
        <p style="font-size:20px;">{{ question }}</p>
        <input name="answer" type="number" required style="font-size:18px;padding:5px;" />
        <button type="submit" style="font-size:18px;">تحقق</button>
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <p style="color:red;">{{ messages[0] }}</p>
      {% endif %}
    {% endwith %}
    </body></html>
    ''', question=question)

@app.route('/security/verify', methods=['POST'])
def verify_captcha():
    try:
        user_answer = int(request.form.get('answer',''))
    except:
        flash("أدخل رقماً صحيحاً.")
        return redirect(url_for('security_challenge'))

    if user_answer == session.get('captcha_answer'):
        session['captcha_verified'] = True
        # Redirect to superadmin login by default
        return redirect(url_for('superadmin_login'))
    else:
        flash('الإجابة خاطئة، حاول مرة أخرى.')
        return redirect(url_for('security_challenge'))

# ===== SuperAdmin login & panel =====

@app.route('/superadmin/login', methods=['GET','POST'])
def superadmin_login():
    if not session.get('captcha_verified'):
        return redirect(url_for('security_challenge'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = SuperAdmin.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('superadmin_panel'))
        else:
            flash("اسم المستخدم أو كلمة المرور خاطئة")
            return redirect(url_for('superadmin_login'))
    return render_template_string('''
    <html><head><title>دخول السوبر أدمن</title></head><body style="background:#000;color:#0f0;font-family:monospace;text-align:center;">
    <h1>تسجيل دخول السوبر أدمن</h1>
    <form method="POST">
        <input name="username" placeholder="اسم المستخدم" required />
        <input name="password" type="password" placeholder="كلمة المرور" required />
        <button type="submit">دخول</button>
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <p style="color:red;">{{ messages[0] }}</p>
      {% endif %}
    {% endwith %}
    </body></html>
    ''')

@app.route('/superadmin/panel')
@login_required
def superadmin_panel():
    if not getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('admin_login'))

    admins = AdminUser.query.all()
    return render_template_string('''
<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8" />
<title>لوحة السوبر أدمن</title></head><body style="background:#000;color:#0f0;font-family:monospace;padding:20px;">
<h1>لوحة تحكم السوبر أدمن</h1>
<p><a href="{{ url_for('logout') }}" style="color:#f00;">تسجيل خروج</a></p>
<h2>إنشاء حساب إداري جديد</h2>
<form method="POST" action="{{ url_for('create_admin') }}">
  <input name="username" placeholder="اسم المستخدم" required />
  <input name="password" type="password" placeholder="كلمة المرور" required />
  <input name="max_accounts" type="number" min="1" value="3" required />
  <button type="submit">إنشاء</button>
</form>

<h2>قائمة الأعضاء الإداريين</h2>
<table border="1" cellpadding="5" cellspacing="0" style="width:100%;color:#0f0;">
  <tr><th>اسم المستخدم</th><th>الحد الأقصى لحسابات البوت</th></tr>
  {% for admin in admins %}
    <tr><td>{{ admin.username }}</td><td>{{ admin.max_accounts }}</td></tr>
  {% else %}
    <tr><td colspan="2">لا يوجد أعضاء.</td></tr>
  {% endfor %}
</table>
</body></html>
''', admins=admins)

@app.route('/superadmin/create_admin', methods=['POST'])
@login_required
def create_admin():
    if not getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('admin_login'))

    username = request.form.get('username')
    password = request.form.get('password')
    max_accounts = int(request.form.get('max_accounts', 3))

    if AdminUser.query.filter_by(username=username).first():
        flash('اسم المستخدم موجود مسبقاً')
        return redirect(url_for('superadmin_panel'))

    new_admin = AdminUser(username=username, password=password, max_accounts=max_accounts)
    db.session.add(new_admin)
    db.session.commit()
    flash('تم إنشاء حساب إداري جديد')
    return redirect(url_for('superadmin_panel'))

# ===== Admin login & dashboard =====

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if not session.get('captcha_verified'):
        return redirect(url_for('security_challenge'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash("اسم المستخدم أو كلمة المرور خاطئة")
            return redirect(url_for('admin_login'))
    return render_template_string('''
<html><head><title>دخول الأدمن</title></head><body style="background:#000;color:#0f0;font-family:monospace;text-align:center;">
<h1>تسجيل دخول الأدمن</h1>
<form method="POST">
  <input name="username" placeholder="اسم المستخدم" required />
  <input name="password" type="password" placeholder="كلمة المرور" required />
  <button type="submit">دخول</button>
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <p style="color:red;">{{ messages[0] }}</p>
  {% endif %}
{% endwith %}
</body></html>
''')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('superadmin_panel'))

    bots = BotAccount.query.filter_by(owner_id=current_user.id).all()
    return render_template_string('''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8" />
<title>لوحة تحكم الأدمن</title></head>
<body style="background:#000;color:#0f0;font-family:monospace;padding:20px;">
<h1>لوحة تحكم الأدمن</h1>
<p>مرحباً، {{ current_user.username }} | <a href="{{ url_for('logout') }}" style="color:#f00;">تسجيل خروج</a></p>

<h2>حسابات البوت المخصصة لك (الحد الأقصى: {{ max_accounts }})</h2>
<table border="1" cellpadding="5" cellspacing="0" style="width:100%;color:#0f0;">
  <tr><th>UID</th><th>كلمة المرور</th><th>إزالة</th></tr>
  {% for bot in bots %}
    <tr>
      <td>{{ bot.uid }}</td>
      <td>{{ bot.password }}</td>
      <td>
        <form method="POST" action="{{ url_for('delete_bot', bot_id=bot.id) }}">
          <button type="submit">حذف</button>
        </form>
      </td>
    </tr>
  {% else %}
    <tr><td colspan="3">لا يوجد حسابات بوت مضافة.</td></tr>
  {% endfor %}
</table>

<h3>إضافة حساب بوت جديد</h3>
<form method="POST" action="{{ url_for('add_bot') }}">
  <label>UID:</label>
  <input name="uid" required />
  <label>كلمة المرور:</label>
  <input name="password" required />
  <button type="submit">إضافة</button>
</form>
</body>
</html>
''', bots=bots, max_accounts=current_user.max_accounts)

@app.route('/admin/add_bot', methods=['POST'])
@login_required
def add_bot():
    if getattr(current_user, 'is_superadmin', False):
        return redirect(url_for('superadmin_panel'))

    uid = request.form.get('uid')
    password = request.form.get('password')

    count = BotAccount.query.filter_by(owner_id=current_user.id).count()
    if count >= current_user.max_accounts:
        flash('وصلت للحد الأقصى من حسابات البوت')
        return redirect(url_for('admin_dashboard'))

    if BotAccount.query.filter_by(uid=uid).first():
        flash('الحساب موجود مسبقاً')
        return redirect(url_for('admin_dashboard'))

    new_bot = BotAccount(uid=uid, password=password, owner_id=current_user.id)
    db.session.add(new_bot)
    db.session.commit()
    flash('تم إضافة حساب بوت جديد')
    return redirect(url_for('admin_dashboard'))

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('captcha_verified', None)
    flash('تم تسجيل الخروج')
    return redirect(url_for('admin_login'))

@app.before_first_request
def setup():
    db.create_all()
    if not SuperAdmin.query.filter_by(username='superadmin').first():
        superadmin = SuperAdmin(username='superadmin', password='superpass')
        db.session.add(superadmin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
