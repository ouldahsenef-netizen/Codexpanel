from flask import Flask, request, make_response, render_template
import requests
import time
from requests.exceptions import RequestException, Timeout
from flask_cors import CORS
from functools import wraps

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 🔒 إعداد API Key
API_KEY = "BNGX_API"

# رابط الـ API الخارجي
LIKES_API_TEMPLATE = "http://85.215.131.70:14062/like?uid={uid}&server_name={region}&key=diamondxpress"
VISIT_API_TEMPLATE = "https://visit-ivory.vercel.app/send_visit?player_id={uid}&server={region}"

# ------------------ Helper: إرجاع رسالة نصية ------------------
def text_response(msg, status=200):
    resp = make_response(str(msg).strip() + "\n", status)
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp

# ------------------ حماية API Key ------------------
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-KEY") or request.args.get("api_key")
        if key != API_KEY:
            return text_response("🚫 وصول مرفوض! المفتاح غير صحيح أو مفقود.", 403)
        return f(*args, **kwargs)
    return decorated

# ------------------ تنظيف الـ payload ------------------
def normalize_payload(payload):
    def safe_int(v):
        try:
            if v is None: return 0
            if isinstance(v, (int, float)): return int(v)
            s = str(v).strip()
            digits = "".join(ch for ch in s if ch.isdigit())
            return int(digits) if digits else 0
        except: return 0

    name = payload.get("PlayerNickname") or payload.get("player_name") or "Unknown"
    return {
        "player_name": name,
        "likes_added": payload.get("LikesGivenByAPI", 0),
        "before": payload.get("LikesbeforeCommand", "N/A"),
        "after": payload.get("LikesafterCommand", "N/A"),
        "status": payload.get("status", "N/A"),
        "remains": payload.get("remains", "N/A")
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_likes', methods=['POST'])
@require_api_key
def add_likes():
    start_time = time.time()
    try:
        data = request.get_json(force=True, silent=False)
        if not data or 'id' not in data or 'region' not in data:
            return text_response("❌ Error: Missing required fields 'id' and 'region' in JSON.", 400)

        player_id = str(data['id']).strip()
        region = str(data['region']).upper().strip()

        if not player_id:
            return text_response("❌ Error: Player ID cannot be empty.", 400)
        if region not in ["ME", "IND"]:
            return text_response("❌ Error: Invalid region. Use 'ME' or 'IND'.", 400)

        api_url = LIKES_API_TEMPLATE.format(uid=player_id, region=region)

        try:
            resp = requests.get(api_url, timeout=25)
        except Timeout:
            return text_response("⏳ Connection timeout with like server. Please try again later.", 504)
        except RequestException:
            return text_response("🚫 Failed to connect to like server. Please try again.", 502)

        if resp.status_code != 200:
            return text_response(f"⚠️ Like server returned status {resp.status_code}.\n{resp.text}", 502)

        try:
            payload = resp.json()
        except ValueError:
            return text_response("❌ Invalid response from like server. Expected JSON format.", 502)

        # ✅ قراءة القيم الجديدة من الرد
        player_name = payload.get("PlayerNickname", "Unknown")
        likes_before = payload.get("LikesbeforeCommand", "N/A")
        likes_after = payload.get("LikesafterCommand", "N/A")
        likes_added = payload.get("LikesGivenByAPI", 0)
        remains = payload.get("remains", "N/A")
        message = payload.get("message", "No message provided.")
        status = payload.get("status", "N/A")

        result_text = f"""
{'💖'*3} LIKE OPERATION RESULT {'💖'*3}

👤 Player: {player_name}
🆔 UID: {player_id}
💌 Likes Added: {likes_added}
💖 Before Command: {likes_before}
💖 After Command: {likes_after}
📜 Message: {message}
📊 Status: {status}
💡 Remaining: {remains}
⏱️ Execution Time: {round(time.time() - start_time, 3)} sec
📅 Executed At: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
"""

        return text_response(result_text, 200)

    except Exception as e:
        return text_response(f"⚠️ Unexpected server error: {str(e)}", 500)

# ------------------ روت جديد: add_visit ------------------
@app.route('/api/add_visit', methods=['POST'])
@require_api_key
def add_visit():
    start_time = time.time()
    try:
        data = request.get_json(force=True, silent=False)
        if not data or 'id' not in data or 'region' not in data:
            return text_response("❌ Error: Missing required fields 'id' and 'region' in JSON.", 400)

        player_id = str(data['id']).strip()
        region = str(data['region']).upper().strip()

        if not player_id:
            return text_response("❌ Error: Player ID cannot be empty.", 400)
        if region not in ["ME", "IND"]:
            return text_response("❌ Error: Invalid region. Use 'ME' or 'IND'.", 400)

        api_url = VISIT_API_TEMPLATE.format(uid=player_id, region=region)

        try:
            resp = requests.get(api_url, timeout=25)
        except Timeout:
            return text_response("⏳ Connection timeout with visit server. Please try again later.", 504)
        except RequestException:
            return text_response("🚫 Failed to connect to visit server. Please try again.", 502)

        if resp.status_code != 200:
            return text_response(f"⚠️ Visit server returned status {resp.status_code}.\n{resp.text}", 502)

        try:
            payload = resp.json()
        except ValueError:
            return text_response("❌ Invalid response from visit server. Expected JSON format.", 502)

        visits_added = payload.get("visits_added", 0)

        result_text = f"""
{'👁️'*3} VISIT OPERATION RESULT {'👁️'*3}

👤 Player ID: {player_id}
🌍 Region: {region}
📈 Visits Added: {visits_added}
⏱️ Execution Time: {round(time.time() - start_time, 3)} sec
📅 Executed At: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
"""
        return text_response(result_text, 200)

    except Exception as e:
        return text_response(f"⚠️ Unexpected server error: {str(e)}", 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
