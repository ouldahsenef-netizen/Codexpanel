from flask import Flask, render_template_string, request, jsonify, abort, Response
import json
import hashlib
import requests
from functools import wraps

app = Flask(__name__)

# مفتاح سري لتوليد الهاش
SECRET_KEY = "your_secret_key_here_change_in_production"

# ديكورات للحماية
def require_no_debug_tools(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_agent = request.headers.get('User-Agent', '').lower()
        if 'devtools' in user_agent or 'postman' in user_agent or 'curl' in user_agent:
            abort(403, description="غير مسموح باستخدام أدوات التطوير")
        return f(*args, **kwargs)
    return decorated_function

def prevent_html_scraping(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if isinstance(response, str):
            protected_html = add_html_protection(response)
            return Response(protected_html, content_type='text/html; charset=utf-8')
        
        return response
    return decorated_function

def add_html_protection(html):
    protection_script = """
    <script>
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        showProtectionMessage('غير مسموح بالنقر بزر الماوس الأيمن');
    });
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        showProtectionMessage('غير مسموح بنسخ النص');
    });
    document.addEventListener('cut', function(e) {
        e.preventDefault();
        showProtectionMessage('غير مسموح بقص النص');
    });
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        showProtectionMessage('غير مسموح بسحب النص');
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12' || 
            (e.ctrlKey && e.shiftKey && e.key === 'I') || 
            (e.ctrlKey && e.key === 'u') ||
            (e.ctrlKey && e.shiftKey && e.key === 'C') ||
            (e.ctrlKey && e.shiftKey && e.key === 'J')) {
            e.preventDefault();
            showProtectionMessage('غير مسموح باستخدام أدوات المطورين');
        }
    });
    function showProtectionMessage(message) {
        const existingMsg = document.getElementById('protection-message');
        if (existingMsg) {
            existingMsg.remove();
        }
        const msgDiv = document.createElement('div');
        msgDiv.id = 'protection-message';
        msgDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #d63031;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        msgDiv.textContent = message;
        document.body.appendChild(msgDiv);
        setTimeout(() => {
            if (msgDiv.parentNode) {
                msgDiv.parentNode.removeChild(msgDiv);
            }
        }, 3000);
    }
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        body {
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        input, textarea {
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
            user-select: text;
        }
    `;
    document.head.appendChild(style);
    </script>
    """
    if '</body>' in html:
        html = html.replace('</body>', protection_script + '</body>')
    else:
        html += protection_script
    return html

def generate_hash(data):
    data_str = json.dumps(data, sort_keys=True) + SECRET_KEY
    return hashlib.sha256(data_str.encode()).hexdigest()

def validate_access_token(token):
    if not token or len(token) != 64:
        return False
    try:
        int(token, 16)
        return True
    except ValueError:
        return False

def call_add_items_api(access_token, uids):
    try:
        encrypt_url = "https://additmesacces.vercel.app/encrypt_multiple"
        encrypt_params = {
            "uids": ",".join(uids)
        }
        encrypt_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        encrypt_response = requests.get(
            encrypt_url,
            params=encrypt_params,
            headers=encrypt_headers,
            timeout=30
        )
        if encrypt_response.status_code != 200:
            return {
                "error": f"فشل في تشفير البيانات: {encrypt_response.text}",
                "encrypt_status": encrypt_response.status_code
            }, False
        encrypt_data = encrypt_response.json()
        if encrypt_data.get('status') != 'success':
            return {
                "error": f"خطأ في التشفير: {encrypt_data.get('error', 'Unknown error')}"
            }, False
        encrypted_uids = encrypt_data.get('encrypted_data')
        if not encrypted_uids:
            return {"error": "لم يتم الحصول على بيانات مشفرة"}, False
        add_items_url = "https://additmesacces.vercel.app/additems"
        add_items_params = {
            "data": encrypted_uids,
            "access_token": access_token
        }
        add_items_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Authorization': f'Bearer {access_token}'
        }
        add_items_response = requests.get(
            add_items_url,
            params=add_items_params,
            headers=add_items_headers,
            timeout=30
        )
        api_response = {
            "encrypt_step": {
                "status_code": encrypt_response.status_code,
                "response": encrypt_data
            },
            "add_items_step": {
                "status_code": add_items_response.status_code,
                "response_text": add_items_response.text
            },
            "encrypted_data": encrypted_uids
        }
        return api_response, add_items_response.status_code == 200
    except requests.exceptions.RequestException as e:
        return {"error": f"خطأ في الاتصال: {str(e)}"}, False
    except Exception as e:
        return {"error": f"خطأ غير متوقع: {str(e)}"}, False

# HTML template as string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9346359398684204"
     crossorigin="anonymous"></script>

    <title>موقع إضافة العناصر الفاخر</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');
        :root {
            --primary: #6c5ce7;
            --primary-dark: #5649c0;
            --secondary: #a29bfe;
            --accent: #fd79a8;
            --dark: #2d3436;
            --light: #f7f7f7;
            --success: #00b894;
            --warning: #fdcb6e;
            --error: #d63031;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Tajawal', sans-serif;
        }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        input, textarea {
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
            user-select: text;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            text-align: center;
            padding: 40px 0;
            position: relative;
        }
        .logo {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(45deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            animation: glow 2s infinite alternate;
        }
        @keyframes glow {
            from {
                text-shadow: 0 0 10px rgba(108, 92, 231, 0.5);
            }
            to {
                text-shadow: 0 0 20px rgba(108, 92, 231, 0.8), 0 0 30px rgba(253, 121, 168, 0.6);
            }
        }
        .subtitle {
            font-size: 1.2rem;
            color: var(--secondary);
            margin-bottom: 30px;
        }
        .buttons-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            position: relative;
            overflow: hidden;
        }
        .btn-primary {
            background: linear-gradient(45deg, var(--primary), var(--primary-dark));
            color: white;
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
        }
        .btn-secondary {
            background: linear-gradient(45deg, var(--accent), #e84393);
            color: white;
            box-shadow: 0 5px 15px rgba(253, 121, 168, 0.4);
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.6);
        }
        .btn:active {
            transform: translateY(1px);
        }
        .btn::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        .btn:hover::after {
            left: 100%;
        }
        .form-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px auto;
            max-width: 800px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: fadeIn 1s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .form-title {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.8rem;
            color: var(--secondary);
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--secondary);
        }
        input {
            width: 100%;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.05);
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.3);
        }
        .items-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        @media (max-width: 768px) {
            .items-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .btn {
                padding: 12px 20px;
                font-size: 1rem;
            }
        }
        .submit-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, var(--success), #00a085);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 184, 148, 0.4);
        }
        .submit-btn:disabled {
            background: #636e72;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .spinner {
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 5px solid var(--primary);
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .result {
            display: none;
            text-align: center;
            padding: 20px;
            margin-top: 20px;
            border-radius: 10px;
            font-weight: 500;
        }
        .success {
            background: rgba(0, 184, 148, 0.2);
            border: 1px solid var(--success);
            color: var(--success);
        }
        .error {
            background: rgba(214, 48, 49, 0.2);
            border: 1px solid var(--error);
            color: var(--error);
        }
        .floating-elements {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        .floating-element {
            position: absolute;
            background: rgba(108, 92, 231, 0.1);
            border-radius: 50%;
            animation: float 15s infinite linear;
        }
        @keyframes float {
            0% {
                transform: translate(0, 0) rotate(0deg);
            }
            100% {
                transform: translate(100px, 100px) rotate(360deg);
            }
        }
        footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: var(--secondary);
            font-size: 0.9rem;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .profile-btn {
            background: linear-gradient(45deg, #0984e3, #74b9ff);
            margin-top: 15px;
            width: 100%;
        }
        .app-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .app-btn {
            flex: 1;
            padding: 12px;
            font-size: 0.9rem;
        }
        .android-btn {
            background: linear-gradient(45deg, #3ddc84, #34a853);
        }
        .web-btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
        }
        .api-status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        .api-success {
            background: rgba(0, 184, 148, 0.1);
            border: 1px solid var(--success);
        }
        .api-error {
            background: rgba(214, 48, 49, 0.1);
            border: 1px solid var(--error);
        }
        .progress-container {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            margin: 20px 0;
            overflow: hidden;
            display: none;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            border-radius: 4px;
            width: 0%;
            transition: width 0.3s ease;
            position: relative;
        }
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        }
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        .progress-steps {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            font-size: 0.8rem;
            color: var(--secondary);
        }
        .step {
            text-align: center;
            flex: 1;
        }
        .step.active {
            color: var(--primary);
            font-weight: bold;
        }
        .step.completed {
            color: var(--success);
        }
    </style>
</head>
<body>
    <div class="floating-elements">
        <div class="floating-element" style="width: 100px; height: 100px; top: 10%; left: 5%;"></div>
        <div class="floating-element" style="width: 150px; height: 150px; top: 60%; left: 80%;"></div>
        <div class="floating-element" style="width: 70px; height: 70px; top: 80%; left: 10%;"></div>
        <div class="floating-element" style="width: 120px; height: 120px; top: 20%; left: 70%;"></div>
    </div>
    <div class="container">
        <header>
            <h1 class="logo">إضافة العناصر النادرة</h1>
            <p class="subtitle">Official Website and Community</p>
            <div class="buttons-container">
                <a href="https://help.garena.com/" class="btn btn-primary" target="_blank">
                    <span>جلب اكسس توكن</span>
                </a>
                <a href="https://items.kibomodz.online/?mode=2&q=itemType%3APET" class="btn btn-secondary" target="_blank">
                    <span>جلب id العناصر</span>
                </a>
            </div>
        </header>
        <div class="form-container">
            <h2 class="form-title">إملاء الخانات من فضلك</h2>
            <div class="input-group">
                <label for="access_token">اكسس توكن</label>
                <input type="text" id="access_token" placeholder="أدخل التوكن الخاص بك">
            </div>
            <div class="input-group">
                <label>معرفات العناصر (12 عنصر)</label>
                <div class="items-grid">
                    {% for i in range(1, 13) %}
                    <input type="text" id="item_{{ i }}" placeholder="ID {{ i }}">
                    {% endfor %}
                </div>
            </div>
            <div class="progress-container" id="progress-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
            <div class="progress-steps" id="progress-steps">
                <div class="step" id="step-1">جاري التحقق</div>
                <div class="step" id="step-2">جاري التشفير</div>
                <div class="step" id="step-3">جاري الإرسال</div>
                <div class="step" id="step-4">جاري المعالجة</div>
                <div class="step" id="step-5">مكتمل</div>
            </div>
            <button class="submit-btn pulse" id="submit-btn">بدء الإضافة</button>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>جاري إضافة العناصر، الرجاء الانتظار...</p>
            </div>
            <div class="result" id="result"></div>
        </div>
        <footer>
            <p>Copyright Garena Online. Trademarks Belong to their respective owners. All right reserved</p>
        </footer>
    </div>
    <script>
        const FREE_FIRE_LINKS = {
            android: 'intent://play/freefire#Intent;package=com.dts.freefireth;scheme=freefire;end;',
            ios: 'freefire://',
            web: 'https://ff.garena.com/',
            playstore: 'https://play.google.com/store/apps/details?id=com.dts.freefireth'
        };
        document.addEventListener('DOMContentLoaded', function() {
            const submitBtn = document.getElementById('submit-btn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            const progressSteps = document.querySelectorAll('.step');
            enableAdvancedProtection();
            submitBtn.addEventListener('click', async function() {
                const accessToken = document.getElementById('access_token').value;
                const itemIds = [];
                for (let i = 1; i <= 12; i++) {
                    const itemId = document.getElementById('item_' + i).value;
                    if (itemId) {
                        itemIds.push(itemId);
                    }
                }
                if (!validateInputs(accessToken, itemIds)) {
                    return;
                }
                submitBtn.style.display = 'none';
                progressContainer.style.display = 'block';
                loading.style.display = 'block';
                result.style.display = 'none';
                try {
                    await startAddingProcess(accessToken, itemIds);
                } catch (error) {
                    loading.style.display = 'none';
                    progressContainer.style.display = 'none';
                    submitBtn.style.display = 'block';
                    showResult('error', 'حدث خطأ في الاتصال بالخادم: ' + error.message);
                }
            });
            function validateInputs(accessToken, itemIds) {
                if (!accessToken) {
                    showResult('error', 'يرجى إدخال التوكن');
                    return false;
                }
                if (accessToken.length !== 64) {
                    showResult('error', 'التوكن غير صالح - يجب أن يكون 64 حرفاً');
                    return false;
                }
                if (itemIds.length !== 12) {
                    showResult('error', 'يرجى إدخال 12 معرف عنصر');
                    return false;
                }
                for (let i = 0; i < itemIds.length; i++) {
                    if (!/^\d{10}$/.test(itemIds[i])) {
                        showResult('error', `معرف العنصر ${i+1} غير صالح - يجب أن يكون 10 أرقام`);
                        return false;
                    }
                }
                return true;
            }
            async function startAddingProcess(accessToken, itemIds) {
                updateProgress(1, 20, 'جاري التحقق من البيانات...');
                await simulateDelay(1000);
                updateProgress(2, 40, 'جاري تشفير البيانات عبر الخادم...');
                await simulateDelay(1000);
                updateProgress(3, 60, 'جاري إرسال البيانات إلى خادم فري فاير...');
                const params = new URLSearchParams({
                    access_token: accessToken,
                    item_ids: itemIds.join(',')
                });
                const response = await fetch('/submit_get?' + params.toString(), {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                const data = await response.json();
                updateProgress(4, 80, 'جاري معالجة الاستجابة...');
                await simulateDelay(1500);
                updateProgress(5, 100, 'اكتملت العملية بنجاح!');
                await simulateDelay(500);
                loading.style.display = 'none';
                progressContainer.style.display = 'none';
                if (data.status === 'success' || data.status === 'partial_success') {
                    showResult('success', data.message, data.api_status, true);
                    console.log('API Response Details:', data.api_response);
                } else {
                    submitBtn.style.display = 'block';
                    showResult('error', data.error || 'حدث خطأ غير متوقع');
                }
            }
            function updateProgress(step, percentage, message) {
                progressBar.style.width = percentage + '%';
                progressSteps.forEach((stepElement, index) => {
                    if (index + 1 < step) {
                        stepElement.classList.add('completed');
                        stepElement.classList.remove('active');
                    } else if (index + 1 === step) {
                        stepElement.classList.add('active');
                        stepElement.classList.remove('completed');
                    } else {
                        stepElement.classList.remove('active', 'completed');
                    }
                });
                const loadingText = loading.querySelector('p');
                if (loadingText) {
                    loadingText.textContent = message;
                }
            }
            function simulateDelay(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
            function showResult(type, message, apiStatus = null, showProfileButton = false) {
                result.className = 'result ' + type;
                let content = `<p>${message}</p>`;
                if (apiStatus) {
                    const statusClass = apiStatus.success ? 'api-success' : 'api-error';
                    const statusText = apiStatus.success ? '✅ تمت العملية بنجاح' : '❌ حدث خطأ';
                    content += `
                        <div class="api-status ${statusClass}">
                            <strong>حالة العملية:</strong> ${statusText}<br>
                            <strong>التشفير:</strong> ${apiStatus.encrypt_status || 'N/A'}<br>
                            <strong>الإضافة:</strong> ${apiStatus.add_items_status || 'N/A'}<br>
                            ${apiStatus.details ? `<small>${apiStatus.details}</small>` : ''}
                        </div>
                    `;
                }
                result.innerHTML = content;
                result.style.display = 'block';
                if (showProfileButton) {
                    const buttonsContainer = document.createElement('div');
                    buttonsContainer.className = 'app-buttons';
                    const androidBtn = document.createElement('button');
                    androidBtn.textContent = 'فتح فري فاير (أندرويد)';
                    androidBtn.className = 'submit-btn app-btn android-btn';
                    androidBtn.addEventListener('click', function() {
                        openFreeFire('android');
                    });
                    const webBtn = document.createElement('button');
                    webBtn.textContent = 'موقع فري فاير (ويب)';
                    webBtn.className = 'submit-btn app-btn web-btn';
                    webBtn.addEventListener('click', function() {
                        openFreeFire('web');
                    });
                    buttonsContainer.appendChild(androidBtn);
                    buttonsContainer.appendChild(webBtn);
                    result.appendChild(buttonsContainer);
                }
            }
            function openFreeFire(platform) {
                if (platform === 'android') {
                    window.location.href = FREE_FIRE_LINKS.android;
                    setTimeout(() => {
                        window.open(FREE_FIRE_LINKS.playstore, '_blank');
                    }, 1000);
                } else {
                    window.open(FREE_FIRE_LINKS.web, '_blank');
                }
            }
            function enableAdvancedProtection() {
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'F12' || 
                        (e.ctrlKey && e.shiftKey && e.key === 'I') || 
                        (e.ctrlKey && e.key === 'u') ||
                        (e.ctrlKey && e.shiftKey && e.key === 'C') ||
                        (e.ctrlKey && e.shiftKey && e.key === 'J')) {
                        e.preventDefault();
                        showProtectionMessage('غير مسموح باستخدام أدوات المطورين');
                    }
                });
                document.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    showProtectionMessage('غير مسموح بالنقر بزر الماوس الأيمن');
                });
                document.addEventListener('copy', function(e) {
                    e.preventDefault();
                    showProtectionMessage('غير مسموح بنسخ النص');
                });
                document.addEventListener('cut', function(e) {
                    e.preventDefault();
                    showProtectionMessage('غير مسموح بقص النص');
                });
            }
            function showProtectionMessage(message) {
                const existingMsg = document.getElementById('protection-message');
                if (existingMsg) {
                    existingMsg.remove();
                }
                const msgDiv = document.createElement('div');
                msgDiv.id = 'protection-message';
                msgDiv.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #d63031;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    z-index: 10000;
                    font-weight: bold;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                    animation: slideIn 0.3s ease;
                `;
                msgDiv.textContent = message;
                document.body.appendChild(msgDiv);
                setTimeout(() => {
                    if (msgDiv.parentNode) {
                        msgDiv.parentNode.removeChild(msgDiv);
                    }
                }, 3000);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
@require_no_debug_tools
@prevent_html_scraping
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/additems')
@require_no_debug_tools
def add_items():
    data = request.args.get('data')
    access_token = request.args.get('access_token')
    if not data or not access_token:
        return jsonify({"error": "بيانات غير مكتملة"}), 400
    response_data = {
        "status": "success",
        "message": "تمت إضافة العناصر بنجاح",
        "data_received": data,
        "token": access_token[:10] + "..."
    }
    return jsonify(response_data)

@app.route('/encrypt_multiple')
@require_no_debug_tools
def encrypt_multiple():
    uids = request.args.get('uids', '')
    if not uids:
        return jsonify({"error": "لم يتم تقديم أي معرفات"}), 400
    uid_list = uids.split(',')
    response_data = {
        "status": "success",
        "encrypted_data": "encrypted_" + hashlib.sha256(uids.encode()).hexdigest()[:32],
        "uids": uid_list
    }
    return jsonify(response_data)

@app.route('/submit_get', methods=['GET'])
@require_no_debug_tools
def submit_get():
    try:
        access_token = request.args.get('access_token')
        item_ids_str = request.args.get('item_ids', '')
        if not access_token or not item_ids_str:
            return jsonify({"error": "بيانات غير مكتملة"}), 400
        if not validate_access_token(access_token):
            return jsonify({"error": "توكن غير صالح - يجب أن يكون 64 حرفاً"}), 400
        item_ids = item_ids_str.split(',')
        if len(item_ids) != 12:
            return jsonify({"error": "يجب إدخال 12 عنصر"}), 400
        for item_id in item_ids:
            if not item_id.isdigit() or len(item_id) != 10:
                return jsonify({"error": f"معرف عنصر غير صالح: {item_id} - يجب أن يكون 10 أرقام"}), 400
        api_response, api_success = call_add_items_api(access_token, item_ids)
        if api_success:
            message = "✅ تمت إضافة العناصر بنجاح! يمكنك الذهاب إلى بروفايل حسابك في فري فاير"
            api_status = {
                "success": True,
                "details": "تمت عملية التشفير والإضافة بنجاح",
                "encrypt_status": api_response.get("encrypt_step", {}).get("status_code"),
                "add_items_status": api_response.get("add_items_step", {}).get("status_code")
            }
        else:
            message = "⚠️ حدث خطأ في عملية الإضافة"
            error_detail = api_response.get('error', 'خطأ غير معروف')
            api_status = {
                "success": False,
                "details": error_detail,
                "encrypt_status": api_response.get("encrypt_step", {}).get("status_code"),
                "add_items_status": api_response.get("add_items_step", {}).get("status_code")
            }
        return jsonify({
            "status": "success" if api_success else "partial_success",
            "message": message,
            "api_response": api_response,
            "api_status": api_status
        })
    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500
