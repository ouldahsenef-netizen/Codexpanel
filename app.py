from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

accounts = {
    "1": {"uid": 4168796933, "password": "FOX_FOX_BY8VI2JJ", "nickname": ""},
    "2": {"uid": 4168796929, "password": "FOX_FOX_YMPSFPKD", "nickname": ""},
    "3": {"uid": 4168796924, "password": "FOX_FOX_9WASGXSJ", "nickname": ""},
}

ADD_URL_TEMPLATE = "https://add-friend-weld.vercel.app/add_friend?token={token}&uid={uid}"
REMOVE_URL_TEMPLATE = "https://remove-self.vercel.app/remove_friend?token={token}&uid={uid}"

@app.route('/')
def index():
    nicknames = {k: v['nickname'] for k, v in accounts.items()}
    return render_template('index.html', nicknames=nicknames)

def get_token(uid, password):
    token_api_url = f"https://jwt-silk-xi.vercel.app/api/oauth_guest?uid={uid}&password={password}"
    token_resp = requests.get(token_api_url)
    token_resp.raise_for_status()
    token_data = token_resp.json()
    token = token_data.get('token')
    if not token:
        raise ValueError("No token received")
    return token

@app.route('/create-acc', methods=['POST'])
def create_acc():
    bot_num = request.json.get('bot')
    nickname = request.json.get('name')

    if bot_num not in accounts:
        return jsonify({"error": "رقم الحساب غير صالح"}), 400

    account = accounts[bot_num]
    try:
        token = get_token(account['uid'], account['password'])
    except Exception as e:
        return jsonify({"error": "فشل في الحصول على التوكن", "details": str(e)}), 500

    change_name_url = f"https://change-name-gray.vercel.app/lvl_up/api/nickname?jwt_token={token}&nickname={nickname}"
    try:
        change_resp = requests.get(change_name_url)
        change_resp.raise_for_status()
        change_data = change_resp.json()
    except Exception as e:
        return jsonify({"error": "فشل في تغيير الاسم", "details": str(e)}), 500

    status_code = change_data.get('status_code')
    if status_code == 200:
        accounts[bot_num]['nickname'] = nickname
        nicknames = {k: v['nickname'] for k, v in accounts.items()}
        return jsonify({"message": "تم إنشاء الحساب بنجاح", "nicknames": nicknames})
    else:
        return jsonify({"message": "الاسم موجود، جرب اسم آخر"}), 400

@app.route('/add-friend', methods=['POST'])
def add_friend():
    bot_num = request.json.get('bot')
    friend_uid = request.json.get('friend_uid')

    if bot_num not in accounts:
        return jsonify({"error": "رقم الحساب غير صالح"}), 400
    if not friend_uid:
        return jsonify({"error": "الرجاء إدخال معرف الصديق (uid)"}), 400

    account = accounts[bot_num]
    try:
        token = get_token(account['uid'], account['password'])
    except Exception as e:
        return jsonify({"error": "فشل في الحصول على التوكن", "details": str(e)}), 500

    add_url = ADD_URL_TEMPLATE.format(token=token, uid=friend_uid)
    try:
        add_resp = requests.get(add_url)
        add_resp.raise_for_status()
        add_data = add_resp.json()
    except Exception as e:
        return jsonify({"error": "فشل في إضافة الصديق", "details": str(e)}), 500

    return jsonify({"message": "تمت إضافة الصديق بنجاح", "response": add_data})

@app.route('/remove-friend', methods=['POST'])
def remove_friend():
    bot_num = request.json.get('bot')
    friend_uid = request.json.get('friend_uid')

    if bot_num not in accounts:
        return jsonify({"error": "رقم الحساب غير صالح"}), 400
    if not friend_uid:
        return jsonify({"error": "الرجاء إدخال معرف الصديق (uid)"}), 400

    account = accounts[bot_num]
    try:
        token = get_token(account['uid'], account['password'])
    except Exception as e:
        return jsonify({"error": "فشل في الحصول على التوكن", "details": str(e)}), 500

    remove_url = REMOVE_URL_TEMPLATE.format(token=token, uid=friend_uid)
    try:
        remove_resp = requests.get(remove_url)
        remove_resp.raise_for_status()
        remove_data = remove_resp.json()
    except Exception as e:
        return jsonify({"error": "فشل في إزالة الصديق", "details": str(e)}), 500

    return jsonify({"message": "تمت إزالة الصديق بنجاح", "response": remove_data})

if __name__ == '__main__':
    app.run(debug=True)
