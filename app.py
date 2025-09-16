from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# حسابات البوت مع الاسم الجديد لكل حساب (يتم تحديثه بعد التغيير)
accounts = {
    "1": {"uid": 4168796916, "password": "FOX_FOX_FYPTO9IK", "nickname": ""},
    "2": {"uid": 4168796926, "password": "FOX_FOX_RFC8FZGV", "nickname": ""},
    "3": {"uid": 4168796933, "password": "FOX_FOX_BY8VI2JJ", "nickname": ""},
}

@app.route('/')
def index():
    # إرسال أسماء الحسابات الحالية للعرض في الصفحة
    nicknames = {k: v['nickname'] for k, v in accounts.items()}
    return render_template('index.html', nicknames=nicknames)

@app.route('/create-acc', methods=['POST'])
def create_acc():
    bot_num = request.json.get('bot')  # "1" أو "2" أو "3"
    nickname = request.json.get('name')

    if bot_num not in accounts:
        return jsonify({"error": "رقم الحساب غير صالح"}), 400

    uid = accounts[bot_num]['uid']
    password = accounts[bot_num]['password']

    # جلب التوكن من API الأول
    token_api_url = f"https://jwt-silk-xi.vercel.app/api/oauth_guest?uid={uid}&password={password}"
    try:
        token_resp = requests.get(token_api_url)
        token_resp.raise_for_status()
        token_data = token_resp.json()
    except Exception as e:
        return jsonify({"error": "فشل في الحصول على التوكن", "details": str(e)}), 500

    token = token_data.get('token')
    if not token:
        return jsonify({"error": "لم يتم استلام التوكن من API"}), 500

    # إرسال طلب تغيير الاسم بالاسم الجديد
    change_name_url = f"https://change-name-gray.vercel.app/lvl_up/api/nickname?jwt_token={token}&nickname={nickname}"
    try:
        change_resp = requests.get(change_name_url)
        change_resp.raise_for_status()
        change_data = change_resp.json()
    except Exception as e:
        return jsonify({"error": "فشل في تغيير الاسم", "details": str(e)}), 500

    status_code = change_data.get('status_code')
    if status_code == 200:
        # حفظ الاسم الجديد في الذاكرة للحساب المعني
        accounts[bot_num]['nickname'] = nickname
        # إرجاع أسماء الحسابات كلها محدثة للواجهة
        nicknames = {k: v['nickname'] for k, v in accounts.items()}
        return jsonify({"message": "تم إنشاء الحساب بنجاح", "nicknames": nicknames})
    else:
        return jsonify({"message": "الاسم موجود، جرب اسم آخر"}), 400

if __name__ == '__main__':
    app.run(debug=True)
