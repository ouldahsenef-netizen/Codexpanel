from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# بيانات الحسابات المخزنة
accounts = {
    "bot1": {"uid": 4168796916, "password": "FOX_FOX_FYPTO9IK"},
    "bot2": {"uid": 4168796926, "password": "FOX_FOX_RFC8FZGV"},
    "bot3": {"uid": 4168796933, "password": "FOX_FOX_BY8VI2JJ"},
}

@app.route('/')
def index():
    return render_template('index.html')  # استدعي ملف index.html

@app.route('/create-acc', methods=['POST'])
def create_acc():
    bot_name = request.json.get('bot')
    nickname = request.json.get('name')

    if bot_name not in accounts:
        return jsonify({"error": "Invalid bot selected"}), 400

    uid = accounts[bot_name]['uid']
    password = accounts[bot_name]['password']

    # جلب التوكن من API الأول
    token_api_url = f"https://jwt-silk-xi.vercel.app/api/oauth_guest?uid={uid}&password={password}"
    try:
        token_resp = requests.get(token_api_url)
        token_resp.raise_for_status()
        token_data = token_resp.json()
    except Exception as e:
        return jsonify({"error": "Failed to get token", "details": str(e)}), 500

    token = token_data.get('token')
    if not token:
        return jsonify({"error": "No token received from API"}), 500

    # إرسال طلب تغيير الاسم بالاسم الجديد
    change_name_url = f"https://change-name-gray.vercel.app/lvl_up/api/nickname?jwt_token={token}&nickname={nickname}"
    try:
        change_resp = requests.get(change_name_url)
        change_resp.raise_for_status()
        change_data = change_resp.json()
    except Exception as e:
        return jsonify({"error": "Failed to change nickname", "details": str(e)}), 500

    # التحقق من حالة الرد
    status_code = change_data.get('status_code')
    if status_code == 200:
        return jsonify({"message": "تم إنشاء الحساب بنجاح"})
    else:
        return jsonify({"message": "الاسم موجود، جرب اسم آخر"}), 400


if __name__ == '__main__':
    app.run(debug=True)
