from flask import Flask, render_template_string, redirect, url_for, request
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MR3SKR System</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
            overflow-x: hidden;
            font-weight: 400;
        }
        
        .code-font {
            font-family: 'JetBrains Mono', monospace;
        }
        
        .glass-card {
            background: rgba(20, 20, 20, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
        }
        
        .platform-card {
            background: rgba(25, 25, 25, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 20px;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .platform-card:hover {
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            background: rgba(30, 30, 30, 0.95);
        }
        
        .accent-color {
            color: #00d4ff;
        }
        
        .accent-bg {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
        }
        
        .token-box {
            background: rgba(15, 15, 15, 0.95);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            word-break: break-all;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            color: #000;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.2);
        }
        
        .status-active {
            color: #00ff88;
        }
        
        .status-inactive {
            color: #ff4444;
        }
        
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .scrollbar-hide {
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        
        .scrollbar-hide::-webkit-scrollbar {
            display: none;
        }
        
        .loading-shimmer {
            background: linear-gradient(90deg, 
                rgba(255,255,255,0.03) 0%, 
                rgba(255,255,255,0.08) 50%, 
                rgba(255,255,255,0.03) 100%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .grid-bg {
            background-image: 
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 30px 30px;
        }
    </style>
</head>
<body class="grid-bg">
    <div class="max-w-6xl mx-auto p-4 md:p-6">
        <!-- Header -->
        <div class="glass-card p-6 mb-8 fade-in">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 class="text-2xl md:text-3xl font-bold gradient-text mb-2">
                        <i class="fas fa-terminal mr-2"></i>SYSTEM ACCESS
                    </h1>
                    <p class="text-gray-400 text-sm">
                        4REAL FUCK ALL TEAMS
                    </p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="flex items-center space-x-2">
                        <div class="pulse-dot"></div>
                        <span class="text-sm status-active">ONLINE</span>
                    </div>
                    <div class="text-gray-500 text-sm code-font">
                        v2.1
                    </div>
                </div>
            </div>
        </div>

        {% if token %}
        <!-- Token Display -->
        <div class="glass-card p-6 mb-8 fade-in">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <div>
                    <h2 class="text-xl font-bold text-white mb-1">
                        <i class="fas fa-key mr-2 accent-color"></i>ACCESS KEY
                    </h2>
                    <p class="text-gray-400 text-sm">Authentication successful</p>
                </div>
                <button onclick="copyToken()" class="btn-primary text-sm px-4 py-2">
                    <i class="far fa-copy mr-2"></i>COPY
                </button>
            </div>
            
            <div class="token-box mb-4">
                <code class="text-sm accent-color">{{token}}</code>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-3 bg-black/30 rounded-lg">
                    <div class="text-lg font-bold text-white mb-1">{{token|length}}</div>
                    <div class="text-xs text-gray-400">LENGTH</div>
                </div>
                <div class="text-center p-3 bg-black/30 rounded-lg">
                    <div class="text-lg font-bold status-active mb-1">VALID</div>
                    <div class="text-xs text-gray-400">STATUS</div>
                </div>
                <div class="text-center p-3 bg-black/30 rounded-lg">
                    <div class="text-lg font-bold text-white mb-1">AES-256</div>
                    <div class="text-xs text-gray-400">TYPE</div>
                </div>
                <div class="text-center p-3 bg-black/30 rounded-lg">
                    <div class="text-lg font-bold text-white mb-1">ACTIVE</div>
                    <div class="text-xs text-gray-400">SESSION</div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Main Content -->
        <div class="glass-card p-6 mb-8">
            <div class="text-center mb-8">
                <h2 class="text-2xl font-bold text-white mb-3">
                    <i class="fas fa-plug mr-2 accent-color"></i>AUTHENTICATION PROVIDERS
                </h2>
                <p class="text-gray-400 max-w-2xl mx-auto">
                    Select provider to initiate authentication sequence
                </p>
            </div>

            <!-- Platform Grid -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <!-- Facebook -->
                <a href="/auth/3" class="platform-card group">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-3">
                            <i class="fab fa-facebook text-blue-400 text-xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-1">Facebook</h3>
                        <p class="text-xs text-gray-400 mb-2">ID: 3</p>
                        <span class="text-xs status-active">
                            <i class="fas fa-circle text-[8px] mr-1"></i> READY
                        </span>
                    </div>
                </a>
                
                <!-- Google -->
                <a href="/auth/8" class="platform-card group">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center mb-3">
                            <i class="fab fa-google text-red-400 text-xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-1">Google</h3>
                        <p class="text-xs text-gray-400 mb-2">ID: 8</p>
                        <span class="text-xs status-active">
                            <i class="fas fa-circle text-[8px] mr-1"></i> READY
                        </span>
                    </div>
                </a>
                
                <!-- Apple -->
                <a href="/auth/10" class="platform-card group">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-12 h-12 rounded-lg bg-gray-500/10 flex items-center justify-center mb-3">
                            <i class="fab fa-apple text-gray-300 text-xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-1">Apple</h3>
                        <p class="text-xs text-gray-400 mb-2">ID: 10</p>
                        <span class="text-xs status-active">
                            <i class="fas fa-circle text-[8px] mr-1"></i> READY
                        </span>
                    </div>
                </a>
                
                <!-- Twitter -->
                <a href="/auth/11" class="platform-card group">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-12 h-12 rounded-lg bg-sky-500/10 flex items-center justify-center mb-3">
                            <i class="fab fa-twitter text-sky-400 text-xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-1">Twitter</h3>
                        <p class="text-xs text-gray-400 mb-2">ID: 11</p>
                        <span class="text-xs status-active">
                            <i class="fas fa-circle text-[8px] mr-1"></i> READY
                        </span>
                    </div>
                </a>
                
                <!-- VK -->
                <a href="/auth/5" class="platform-card group">
                    <div class="flex flex-col items-center text-center">
                        <div class="w-12 h-12 rounded-lg bg-blue-400/10 flex items-center justify-center mb-3">
                            <i class="fab fa-vk text-blue-300 text-xl"></i>
                        </div>
                        <h3 class="font-semibold text-white mb-1">VKontakte</h3>
                        <p class="text-xs text-gray-400 mb-2">ID: 5</p>
                        <span class="text-xs status-active">
                            <i class="fas fa-circle text-[8px] mr-1"></i> READY
                        </span>
                    </div>
                </a>
            </div>
        </div>

        <!-- System Status -->
        <div class="glass-card p-6">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div class="p-4 bg-black/30 rounded-lg">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-gray-400">PROVIDERS</span>
                        <span class="text-sm font-bold text-white">5</span>
                    </div>
                    <div class="h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div class="h-full accent-bg w-full"></div>
                    </div>
                </div>
                
                <div class="p-4 bg-black/30 rounded-lg">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-gray-400">UPTIME</span>
                        <span class="text-sm font-bold status-active">100%</span>
                    </div>
                    <div class="h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div class="h-full bg-green-500 w-full"></div>
                    </div>
                </div>
                
                <div class="p-4 bg-black/30 rounded-lg">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-gray-400">LATENCY</span>
                        <span class="text-sm font-bold text-white">12ms</span>
                    </div>
                    <div class="h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div class="h-full bg-blue-500 w-3/4"></div>
                    </div>
                </div>
                
                <div class="p-4 bg-black/30 rounded-lg">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-gray-400">REQUESTS</span>
                        <span class="text-sm font-bold text-white">256</span>
                    </div>
                    <div class="h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div class="h-full bg-purple-500 w-2/3"></div>
                    </div>
                </div>
            </div>
            
            <div class="border-t border-gray-800 pt-6">
                <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-2">
                            <i class="fas fa-server text-gray-500"></i>
                            <span class="text-sm text-gray-400 code-font">mr3skr@system:~</span>
                        </div>
                    </div>
                    <div class="text-xs text-gray-500">
                        © 2024 SYSTEM INTERFACE
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Optimized animations
        let lastTime = 0;
        const fps = 60;
        
        function copyToken() {
            const token = "{{token}}";
            if (!token) return;
            
            navigator.clipboard.writeText(token).then(() => {
                const btn = event.currentTarget;
                const original = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check mr-2"></i>COPIED';
                btn.style.background = '#00ff88';
                btn.style.color = '#000';
                
                setTimeout(() => {
                    btn.innerHTML = original;
                    btn.style.background = '';
                    btn.style.color = '';
                }, 1500);
            });
        }
        
        // Smooth hover effects
        document.querySelectorAll('.platform-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
        
        // Performance optimized background effect
        function createBackgroundDot() {
            const dot = document.createElement('div');
            dot.style.cssText = `
                position: fixed;
                width: 1px;
                height: 1px;
                background: rgba(0, 212, 255, 0.1);
                border-radius: 50%;
                pointer-events: none;
                z-index: -1;
            `;
            dot.style.left = Math.random() * 100 + 'vw';
            dot.style.top = '-10px';
            
            document.body.appendChild(dot);
            
            const duration = Math.random() * 4000 + 3000;
            const keyframes = [
                { transform: 'translateY(0) scale(1)', opacity: 0 },
                { transform: 'translateY(0) scale(1)', opacity: 0.3 },
                { transform: `translateY(${window.innerHeight + 20}px) scale(0.5)`, opacity: 0 }
            ];
            
            dot.animate(keyframes, {
                duration: duration,
                easing: 'linear'
            }).onfinish = () => dot.remove();
        }
        
        // Reduced particle count for performance
        let dotCount = 0;
        const maxDots = 15;
        
        function manageBackgroundDots() {
            const now = Date.now();
            if (now - lastTime < 1000 / fps) return;
            
            if (dotCount < maxDots) {
                createBackgroundDot();
                dotCount++;
                setTimeout(() => dotCount--, 5000);
            }
            
            lastTime = now;
            requestAnimationFrame(manageBackgroundDots);
        }
        
        // Start background effects
        if (window.innerWidth > 768) {
            manageBackgroundDots();
        }
        
        // Prevent rapid clicking
        let lastClick = 0;
        document.addEventListener('click', (e) => {
            if (e.target.closest('a')) {
                const now = Date.now();
                if (now - lastClick < 1000) {
                    e.preventDefault();
                }
                lastClick = now;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    token = request.args.get('access_token')
    if token:
        token = token.split('?')[0] if '?' in token else token
    return render_template_string(HTML_TEMPLATE, token=token)

@app.route('/auth/<int:platform_id>')
def auth_redirect(platform_id):
    base_url = "https://auth.garena.com/universal/oauth"
    redirect_uri = "https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-ticket.ff.gameid.garena.co.id/oauth/callback_redirect/"
    
    params = {
        'platform': platform_id,
        'response_type': 'code',
        'locale': 'en-SG',
        'client_id': '100067',
        'redirect_uri': redirect_uri
    }
    
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    auth_url = f"{base_url}?{query_string}"
    
    return redirect(auth_url)

@app.route('/callback')
def callback():
    token = request.args.get('access_token')
    if token:
        return redirect(f'/?access_token={token}')
    return redirect('/')

@app.errorhandler(404)
def not_found(e):
    return redirect('/')

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=False, port=5000)
