from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>BNGX PANEL</title>
    <style>
        body {
            background:#0d0d0d;
            color:#00ff99;
            font-family:monospace;
            text-align:center;
            margin:0;
            padding:0;
        }
        .container {
            max-width:600px;
            margin:50px auto;
            padding:20px;
            background:rgba(0,0,0,0.7);
            border-radius:10px;
            box-shadow: 0 0 20px #00ff99;
        }
        .input-field {
            width:100%;
            padding:10px;
            margin:10px 0;
            border-radius:6px;
            border:1px solid #00ff99;
            background:#111;
            color:#00ff99;
            font-size:16px;
        }
        .btn {
            padding:10px 20px;
            border:none;
            border-radius:6px;
            background:linear-gradient(90deg,#ff00ff,#00ffff);
            color:#000;
            font-weight:bold;
            cursor:pointer;
            font-size:16px;
            transition: 0.3s;
        }
        .btn:hover { transform: scale(1.05); }
        #status { margin-top:10px; font-weight:bold; }
        .result-card {
            margin-top:20px;
            text-align:right;
            background: linear-gradient(145deg, rgba(0,255,153,0.2), rgba(0,255,153,0.05));
            border: 1px solid #00ff99;
            padding: 15px;
            border-radius:10px;
            color: #caffd6;
            box-shadow: 0 0 10px #00ff99 inset, 0 0 20px #00ff99;
        }
        .result-key { color:#00ffc1; font-weight:bold; }
        .matrix-canvas {
            position: fixed;
            top:0;
            left:0;
            width:100%;
            height:100%;
            z-index:-1;
        }
    </style>
</head>
<body>
    <canvas id="matrix-canvas" class="matrix-canvas"></canvas>

    <div class="container">
        <h1>BNGX PANEL - Add Likes</h1>
        <input type="text" id="uid" class="input-field" placeholder="ادخل ID اللاعب" />
        <button id="sendBtn" class="btn">Add Likes</button>
        <div id="status"></div>
        <div id="result" class="result-card">هنا ستظهر النتيجة...</div>
    </div>

<script>
// زر Add Likes
document.getElementById("sendBtn").addEventListener("click", async () => {
    const uid = document.getElementById("uid").value.trim();
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");

    if (!uid) {
        statusDiv.innerHTML = "⚠️ يرجى إدخال ID صالح.";
        return;
    }

    statusDiv.innerHTML = "⏳ جاري إرسال الطلب...";
    resultDiv.innerHTML = "جارٍ المعالجة...";

    try {
        const res = await fetch("/api/add_likes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: uid })
        });

        const data = await res.json();

        if (data.error) {
            statusDiv.innerHTML = "❌ حدث خطأ: " + data.error;
            resultDiv.innerHTML = "";
            return;
        }

        statusDiv.innerHTML = "✅ تمت العملية بنجاح!";
        resultDiv.innerHTML = `
            <div><span class="result-key">👤 الاسم:</span> ${data.player_name}</div>
            <div><span class="result-key">🆔 ID:</span> ${data.player_id}</div>
            <div><span class="result-key">👍 اللايكات قبل:</span> ${data.likes_before}</div>
            <div><span class="result-key">✨ اللايكات المضافة:</span> ${data.likes_added}</div>
            <div><span class="result-key">🎯 اللايكات بعد:</span> ${data.likes_after}</div>
            <div><span class="result-key">⏱️ المدة حتى المسموح القادم:</span> ${data.seconds_until_next_allowed} ثانية</div>
        `;
    } catch (err) {
        console.error(err);
        statusDiv.innerHTML = "❌ فشل الاتصال بالخادم.";
        resultDiv.innerHTML = err.message || "خطأ غير معروف";
    }
});

// Matrix Rain
const canvas = document.getElementById('matrix-canvas');
const ctx = canvas.getContext('2d');
let width, height, fontSize=16, columns, drops;

function resizeCanvas() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    columns = Math.floor(width / fontSize);
    drops = Array(columns).fill(1);
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(0,0,0,0.08)';
    ctx.fillRect(0,0,width,height);
    ctx.font = fontSize + "px monospace";
    for(let i=0;i<drops.length;i++){
        const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*';
        const text = charset.charAt(Math.floor(Math.random()*charset.length));
        ctx.fillStyle = '#00ff99';
        ctx.fillText(text, i*fontSize, drops[i]*fontSize);
        if(drops[i]*fontSize>height && Math.random()>0.975) drops[i]=0;
        drops[i]++;
    }
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
setInterval(drawMatrix, 50);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/add_likes", methods=["POST"])
def add_likes():
    try:
        data = request.get_json(force=True)
        uid = data.get("id")
        if not uid:
            return jsonify({"error": "missing id"}), 400

        r = requests.get(f"https://likes-khaki.vercel.app/send_like?player_id={uid}", timeout=75)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
