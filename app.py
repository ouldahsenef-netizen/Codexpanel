from flask import Flask, request, jsonify, render_template
import requests
from requests.exceptions import RequestException, Timeout
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # يسمح بالطلبات من الواجهة إذا احتجت (اختياري)

LIKES_API_TEMPLATE = "https://likes-khaki.vercel.app/send_like?player_id={uid}"

@app.route('/')
def index():
    # تأكد أن لديك index.html داخل مجلد templates
    return render_template('index.html')

@app.route('/api/add_likes', methods=['POST'])
def add_likes():
    """
    تتوقع JSON body: {"id": "<player_id>"}
    تعيد JSON يحتوي على ملخص النتيجة + JSON الخام من الـ API إن وُجد.
    """
    try:
        data = request.get_json(force=True, silent=True)
        if not data or 'id' not in data:
            return jsonify({"success": False, "message": "مطلوب: حقل 'id' في جسم الطلب."}), 400

        player_id = str(data['id']).strip()
        if player_id == "":
            return jsonify({"success": False, "message": "قيمة 'id' فارغة."}), 400

        # بناء رابط الـ API الخارجي
        api_url = LIKES_API_TEMPLATE.format(uid=player_id)

        # نطلب الـ API الخارجي مباشرة (نحدد timeout للسلامة)
        try:
            resp = requests.get(api_url, timeout=10)
        except Timeout:
            return jsonify({"success": False, "message": "انتهى وقت الانتظار عند الاتصال بخدمة اللايكس."}), 504
        except RequestException as e:
            return jsonify({"success": False, "message": f"خطأ في الاتصال بالـ API الخارجي: {str(e)}"}), 502

        # حاول تحويل الرد إلى JSON
        try:
            payload = resp.json()
        except ValueError:
            # إذا لم يكن JSON، نعيد النص الخام
            raw_text = resp.text
            return jsonify({
                "success": False,
                "message": "استجابة الخادم الخارجي لم تكن JSON.",
                "status_code": resp.status_code,
                "raw": raw_text
            }), 502

        # الآن لدينا JSON؛ نُخرج الحقول المهمة التي ذكرتها
        # (نتعامل مع المفاتيح الموجودة أو نضع قيمة افتراضية)
        result = {
            "likes_added": payload.get("likes_added"),
            "likes_after": payload.get("likes_after"),
            "likes_before": payload.get("likes_before"),
            "player_id": payload.get("player_id"),
            "player_name": payload.get("player_name"),
            "seconds_until_next_allowed": payload.get("seconds_until_next_allowed"),
            # نحتفظ أيضاً بالـ JSON الكامل كحقل raw_response
            "raw_response": payload
        }

        # تحديد حالة النجاح بطريقة بسيطة: إن نجا الطلب (200) ووجدنا likes_added على الأقل
        success_flag = resp.ok and (result["likes_added"] is not None)

        return jsonify({
            "success": bool(success_flag),
            "message": "تم الاتصال بخدمة اللايكس." if success_flag else "تم الاتصال بالخدمة لكن لم تحتوي الاستجابة على بيانات متوقعة.",
            "data": result
        }), (200 if success_flag else 207)

    except Exception as e:
        # خطأ غير متوقع
        return jsonify({"success": False, "message": "حدث خطأ في الخادم: " + str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
