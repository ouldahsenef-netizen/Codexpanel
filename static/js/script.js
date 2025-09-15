// Matrix Rain Effect
class MatrixRain {
    constructor() {
        this.canvas = document.getElementById('matrix-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.characters = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        this.charArray = this.characters.split('');
        this.drops = [];
        
        this.resizeCanvas();
        this.init();
        this.animate();
        
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        const columns = Math.floor(this.canvas.width / 14);
        this.drops = [];
        for (let i = 0; i < columns; i++) {
            this.drops[i] = Math.random() * this.canvas.height;
        }
    }
    
    init() {
        const columns = Math.floor(this.canvas.width / 14);
        for (let i = 0; i < columns; i++) {
            this.drops[i] = Math.random() * this.canvas.height;
        }
    }
    
    animate() {
        // Black background with transparency for trail effect
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Green text
        this.ctx.fillStyle = '#00FF41';
        this.ctx.font = '14px Fira Code, monospace';
        
        for (let i = 0; i < this.drops.length; i++) {
            const char = this.charArray[Math.floor(Math.random() * this.charArray.length)];
            const x = i * 14;
            const y = this.drops[i];
            
            this.ctx.fillText(char, x, y);
            
            // Reset drop to top randomly
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            this.drops[i] += 14;
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// API Helper Functions
class APIManager {
    constructor() {
        this.baseURL = '';
        this.bioTokenVerified = false;
        this.itemTokenVerified = false;
    }
    
    async request(method, endpoint, data = null) {
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            config.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(endpoint, config);
            const result = await response.json();
            return { success: response.ok, data: result, status: response.status };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    showResult(title, content, isSuccess = true) {
        const modal = document.getElementById('result-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        
        modalTitle.textContent = title;
        modalTitle.style.color = isSuccess ? '#00ff41' : '#ff0000';
        
        if (typeof content === 'object') {
            // Special handling for outfit and banner responses
            if (title.includes('Outfit')) {
                // Check for various possible image fields in outfit response
                const imageUrl = content.outfit_image || content.image || content.url || 
                                content.outfit || content.data?.image || content.data?.url ||
                                this.extractImageFromMessage(content.message);
                
                if (imageUrl && this.isValidImageUrl(imageUrl)) {
                    modalBody.innerHTML = `
                        <div class="result-content">
                            <img src="${imageUrl}" alt="User Outfit" class="result-image" style="max-width: 100%; border-radius: 10px; margin: 10px 0;"/>
                            <div class="result-details">
                                <h4 style="color: #9932cc; margin-bottom: 10px;">🎮 Outfit Details</h4>
                                <pre>${JSON.stringify(content, null, 2)}</pre>
                            </div>
                        </div>
                    `;
                } else {
                    // If no image found, show formatted message
                    modalBody.innerHTML = `
                        <div class="result-content">
                            <div class="outfit-message">
                                <h4 style="color: #9932cc; margin-bottom: 10px;">👕 Outfit Response</h4>
                                <div class="message-box" style="background: rgba(153, 50, 204, 0.1); border: 1px solid #9932cc; border-radius: 8px; padding: 15px; margin: 10px 0;">
                                    <p style="color: #00ff41; font-family: 'Fira Code', monospace;">${content.message || 'No outfit data available'}</p>
                                </div>
                                <details style="margin-top: 15px;">
                                    <summary style="color: #9932cc; cursor: pointer;">📄 Raw Response</summary>
                                    <pre style="margin-top: 10px; font-size: 12px;">${JSON.stringify(content, null, 2)}</pre>
                                </details>
                            </div>
                        </div>
                    `;
                }
            } else if (title.includes('Banner')) {
                const imageUrl = content.banner_url || content.banner || content.image || content.url ||
                                content.data?.banner || content.data?.image || content.data?.url ||
                                this.extractImageFromMessage(content.message);
                
                if (imageUrl && this.isValidImageUrl(imageUrl)) {
                    modalBody.innerHTML = `
                        <div class="result-content">
                            <img src="${imageUrl}" alt="User Banner" class="result-image" style="max-width: 100%; border-radius: 10px; margin: 10px 0;"/>
                            <div class="result-details">
                                <h4 style="color: #9932cc; margin-bottom: 10px;">🖼️ Banner Details</h4>
                                <pre>${JSON.stringify(content, null, 2)}</pre>
                            </div>
                        </div>
                    `;
                } else {
                    // If no image found, show formatted message
                    modalBody.innerHTML = `
                        <div class="result-content">
                            <div class="banner-message">
                                <h4 style="color: #9932cc; margin-bottom: 10px;">🏆 Banner Response</h4>
                                <div class="message-box" style="background: rgba(153, 50, 204, 0.1); border: 1px solid #9932cc; border-radius: 8px; padding: 15px; margin: 10px 0;">
                                    <p style="color: #00ff41; font-family: 'Fira Code', monospace;">${content.message || 'No banner data available'}</p>
                                </div>
                                <details style="margin-top: 15px;">
                                    <summary style="color: #9932cc; cursor: pointer;">📄 Raw Response</summary>
                                    <pre style="margin-top: 10px; font-size: 12px;">${JSON.stringify(content, null, 2)}</pre>
                                </details>
                            </div>
                        </div>
                    `;
                }
            } else if (title.includes('User Information')) {
                // Beautiful formatting for user info
                const formatUserInfo = (data) => {
                    if (data.basicInfo) {
                        return `
                            <div class="user-info-card">
                                <h4 style="color: #00ff41; margin-bottom: 15px;">👤 Player Information</h4>
                                <div class="info-grid">
                                    <div class="info-item"><span class="label">🎮 Name:</span> <span class="value">${data.basicInfo.nickname || 'N/A'}</span></div>
                                    <div class="info-item"><span class="label">🆔 Player ID:</span> <span class="value">${data.basicInfo.accountId || 'N/A'}</span></div>
                                    <div class="info-item"><span class="label">🏆 Level:</span> <span class="value">${data.basicInfo.level || 'N/A'}</span></div>
                                    <div class="info-item"><span class="label">⭐ EXP:</span> <span class="value">${data.basicInfo.exp || 'N/A'}</span></div>
                                    <div class="info-item"><span class="label">💰 Gold:</span> <span class="value">${data.basicInfo.gold || 'N/A'}</span></div>
                                    <div class="info-item"><span class="label">💎 Diamonds:</span> <span class="value">${data.basicInfo.diamond || 'N/A'}</span></div>
                                </div>
                                <details style="margin-top: 15px;">
                                    <summary style="color: #9932cc; cursor: pointer;">📄 Raw Data</summary>
                                    <pre style="margin-top: 10px; font-size: 12px;">${JSON.stringify(data, null, 2)}</pre>
                                </details>
                            </div>
                        `;
                    }
                    return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                };
                modalBody.innerHTML = formatUserInfo(content);
            } else {
                modalBody.innerHTML = `<pre>${JSON.stringify(content, null, 2)}</pre>`;
            }
        } else {
            // Handle string content - could be URL, encoded data, or text
            if (typeof content === 'string') {
                // Check if it's a direct image URL
                if (this.isValidImageUrl(content)) {
                    modalBody.innerHTML = `
                        <div class="result-content">
                            <img src="${content}" alt="Result Image" class="result-image" style="max-width: 100%; border-radius: 10px; margin: 10px 0; box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);"/>
                        </div>
                    `;
                } else {
                    // Check if string contains a URL
                    const extractedUrl = this.extractImageFromMessage(content);
                    if (extractedUrl) {
                        modalBody.innerHTML = `
                            <div class="result-content">
                                <img src="${extractedUrl}" alt="Result Image" class="result-image" style="max-width: 100%; border-radius: 10px; margin: 10px 0; box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);"/>
                                <details style="margin-top: 15px;">
                                    <summary style="color: #9932cc; cursor: pointer;">📄 Original Response</summary>
                                    <pre style="margin-top: 10px; font-size: 12px; max-height: 300px; overflow-y: auto;">${content}</pre>
                                </details>
                            </div>
                        `;
                    } else {
                        // Handle long text/encoded data
                        if (content.length > 200) {
                            modalBody.innerHTML = `
                                <div class="result-content">
                                    <div class="data-message">
                                        <h4 style="color: #9932cc; margin-bottom: 10px;">📊 Response Data</h4>
                                        <div class="message-box" style="background: rgba(0, 255, 65, 0.05); border: 1px solid #00ff41; border-radius: 8px; padding: 15px; margin: 10px 0; max-height: 400px; overflow-y: auto;">
                                            <pre style="color: #00ff41; font-family: 'Fira Code', monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all;">${content}</pre>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            modalBody.innerHTML = `
                                <div class="result-content">
                                    <p style="color: #00ff41; font-family: 'Fira Code', monospace;">${content}</p>
                                </div>
                            `;
                        }
                    }
                }
            } else {
                modalBody.innerHTML = content;
            }
        }
        
        modal.style.display = 'flex';
    }
    
    // Helper function to check if a URL is a valid image URL
    isValidImageUrl(url) {
        if (!url || typeof url !== 'string') return false;
        // Check for common image extensions
        if (/\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)$/i.test(url)) return true;
        // Check for image-related keywords in URL
        if (url.includes('image') || url.includes('photo') || url.includes('pic') || url.includes('img')) return true;
        // Check for common image hosting domains
        if (url.includes('imgur.com') || url.includes('cloudinary.com') || url.includes('tinypic.com')) return true;
        return false;
    }
    
    // Helper function to extract image URL from message text
    extractImageFromMessage(message) {
        if (!message || typeof message !== 'string') return null;
        
        // Look for URLs with image extensions first
        const imageExtMatch = message.match(/(https?:\/\/[^\s]+\.(jpg|jpeg|png|gif|webp|svg|bmp))/i);
        if (imageExtMatch) return imageExtMatch[0];
        
        // Look for any HTTP/HTTPS URLs
        const allUrls = message.match(/(https?:\/\/[^\s"'<>]+)/gi);
        if (allUrls) {
            for (const url of allUrls) {
                if (this.isValidImageUrl(url)) {
                    return url;
                }
            }
        }
        
        // Special case for data URLs (base64 images)
        const dataUrlMatch = message.match(/(data:image\/[^;]+;base64,[^\s"'<>]+)/i);
        if (dataUrlMatch) return dataUrlMatch[0];
        
        return null;
    }
    
    showStatus(elementId, message, isSuccess = true) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.className = `status-message ${isSuccess ? 'status-success' : 'status-error'}`;
        element.style.display = 'block';
    }
    
    async validateToken(token, type) {
        if (!token.trim()) {
            this.showStatus(`${type}-token-status`, 'Please enter an access token', false);
            return false;
        }
        
        const result = await this.request('POST', '/api/validate-token', { token });
        
        if (result.success && result.data.success) {
            this.showStatus(`${type}-token-status`, '✅ Token verified successfully', true);
            if (type === 'bio') {
                this.bioTokenVerified = true;
                document.getElementById('bio-input-group').style.display = 'block';
            } else if (type === 'item') {
                this.itemTokenVerified = true;
                document.getElementById('item-input-group').style.display = 'block';
            }
            return true;
        } else {
            const message = result.data?.message || result.error || 'Token validation failed';
            this.showStatus(`${type}-token-status`, `❌ ${message}`, false);
            return false;
        }
    }
    
    async updateBio() {
        const token = document.getElementById('bio-token').value.trim();
        const newBio = document.getElementById('new-bio').value.trim();
        
        if (!this.bioTokenVerified) {
            this.showResult('Error', 'Please verify your access token first', false);
            return;
        }
        
        if (!newBio) {
            this.showResult('Error', 'Please enter bio content', false);
            return;
        }
        
        const result = await this.request('POST', '/api/update-bio', {
            accessToken: token,
            newBio: newBio
        });
        
        if (result.success && result.data.success) {
            this.showResult('Bio Updated Successfully', result.data.data || 'Bio has been updated', true);
            document.getElementById('new-bio').value = '';
        } else {
            const message = result.data?.message || result.error || 'Bio update failed';
            this.showResult('Bio Update Failed', message, false);
        }
    }
    
    async injectItems() {
        const token = document.getElementById('item-token').value.trim();
        const itemId = document.getElementById('item-id').value.trim();
        const quantity = parseInt(document.getElementById('quantity').value) || 1;
        
        if (!this.itemTokenVerified) {
            this.showResult('Error', 'Please authenticate your access token first', false);
            return;
        }
        
        if (!itemId) {
            this.showResult('Error', 'Please enter an item ID', false);
            return;
        }
        
        const result = await this.request('POST', '/api/add-items', {
            accessToken: token,
            itemId: itemId,
            quantity: quantity
        });
        
        if (result.success && result.data.success) {
            this.showResult('Items Injected Successfully', result.data.data || 'Items have been added to your profile', true);
            document.getElementById('item-id').value = '';
            document.getElementById('quantity').value = '1';
        } else {
            const message = result.data?.message || result.error || 'Item injection failed';
            this.showResult('Item Injection Status', message, false);
        }
    }
    
    async getUserInfo() {
        const uid = document.getElementById('user-id').value.trim();
        
        if (!uid) {
            this.showResult('Error', 'Please enter a User ID', false);
            return;
        }
        
        const result = await this.request('GET', `/api/user-info/${uid}`);
        
        if (result.success && result.data.success) {
            this.showResult('User Information', result.data.data, true);
        } else {
            const message = result.data?.message || result.error || 'Failed to retrieve user info';
            this.showResult('User Info Error', message, false);
        }
        
        document.getElementById('user-id').value = '';
    }
    
    async sendFriend() {
        const playerId = document.getElementById('friend-player-id').value.trim();
        
        if (!playerId) {
            this.showResult('Error', 'Please enter a Player ID', false);
            return;
        }
        
        const result = await this.request('POST', '/api/send-friend', { playerId });
        
        if (result.success && result.data.success) {
            this.showResult('Friend Request Sent', result.data.data, true);
        } else {
            const message = result.data?.message || result.error || 'Friend request failed';
            this.showResult('Friend Request Error', message, false);
        }
        
        document.getElementById('friend-player-id').value = '';
    }
    
    async getBanner() {
        const uid = document.getElementById('banner-uid').value.trim();
        
        if (!uid) {
            this.showResult('Error', 'Please enter a User ID', false);
            return;
        }
        
        const result = await this.request('GET', `/api/banner/${uid}?key=BNGX`);
        
        if (result.success && result.data.success) {
            // Check if the response contains an image URL
            const bannerData = result.data.data;
            if (typeof bannerData === 'string') {
                // Check if it's a direct image URL
                if (this.isValidImageUrl(bannerData)) {
                    this.showResult('🎯 Banner Information', bannerData, true, 'banner');
                } else if (bannerData.includes('http')) {
                    // Try to extract URL from the response
                    const extractedUrl = this.extractImageFromMessage(bannerData);
                    if (extractedUrl) {
                        this.showResult('🎯 Banner Information', extractedUrl, true, 'banner');
                    } else {
                        this.showResult('🎯 Banner Information', bannerData, true, 'banner');
                    }
                } else {
                    // If it's encoded or text data, show it in a formatted way
                    this.showResult('🎯 Banner Information', bannerData, true, 'banner');
                }
            } else {
                // If it's an object, try to find image URL in it
                if (bannerData && typeof bannerData === 'object') {
                    const imageUrl = bannerData.url || bannerData.image || bannerData.banner_url;
                    if (imageUrl && this.isValidImageUrl(imageUrl)) {
                        this.showResult('🎯 Banner Information', imageUrl, true, 'banner');
                    } else {
                        this.showResult('🎯 Banner Information', bannerData, true, 'banner');
                    }
                } else {
                    this.showResult('🎯 Banner Information', bannerData, true, 'banner');
                }
            }
        } else {
            const message = result.data?.message || result.error || 'Banner request failed';
            this.showResult('Banner Error', message, false);
        }
        
        document.getElementById('banner-uid').value = '';
    }
    
    async sendLikes() {
        const playerId = document.getElementById('like-player-id').value.trim();
        
        if (!playerId) {
            this.showResult('Error', 'Please enter a Player ID', false);
            return;
        }
        
        const result = await this.request('POST', '/api/send-likes', { playerId });
        
        if (result.success && result.data.success) {
            this.showResult('Likes Sent Successfully', result.data.data, true);
        } else {
            const message = result.data?.message || result.error || 'Like request failed';
            this.showResult('Like Request Error', message, false);
        }
        
        document.getElementById('like-player-id').value = '';
    }
    
    async getOutfit() {
        const uid = document.getElementById('outfit-uid').value.trim();
        
        if (!uid) {
            this.showResult('Error', 'Please enter a User ID', false);
            return;
        }
        
        const result = await this.request('GET', `/api/outfit/${uid}?region=me&key=BNGX`);
        
        if (result.success && result.data.success) {
            // Check if the response contains an image URL
            const outfitData = result.data.data;
            if (typeof outfitData === 'string') {
                // Check if it's a direct image URL
                if (this.isValidImageUrl(outfitData)) {
                    this.showResult('👕 Outfit Information', outfitData, true, 'outfit');
                } else if (outfitData.includes('http')) {
                    // Try to extract URL from the response
                    const extractedUrl = this.extractImageFromMessage(outfitData);
                    if (extractedUrl) {
                        this.showResult('👕 Outfit Information', extractedUrl, true, 'outfit');
                    } else {
                        this.showResult('👕 Outfit Information', outfitData, true, 'outfit');
                    }
                } else {
                    // If it's encoded or text data, show it in a formatted way
                    this.showResult('👕 Outfit Information', outfitData, true, 'outfit');
                }
            } else {
                // If it's an object, try to find image URL in it
                if (outfitData && typeof outfitData === 'object') {
                    const imageUrl = outfitData.url || outfitData.image || outfitData.outfit_url;
                    if (imageUrl && this.isValidImageUrl(imageUrl)) {
                        this.showResult('👕 Outfit Information', imageUrl, true, 'outfit');
                    } else {
                        this.showResult('👕 Outfit Information', outfitData, true, 'outfit');
                    }
                } else {
                    this.showResult('👕 Outfit Information', outfitData, true, 'outfit');
                }
            }
        } else {
            const message = result.data?.message || result.error || 'Outfit request failed';
            this.showResult('Outfit Error', message, false);
        }
        
        document.getElementById('outfit-uid').value = '';
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Start Matrix Rain
    new MatrixRain();
    
    // Initialize API Manager
    const api = new APIManager();
    
    // Bio Update Event Listeners
    document.getElementById('verify-bio-token').addEventListener('click', function() {
        const token = document.getElementById('bio-token').value;
        api.validateToken(token, 'bio');
    });
    
    document.getElementById('update-bio').addEventListener('click', function() {
        api.updateBio();
    });
    
    // Item Injection Event Listeners
    document.getElementById('verify-item-token').addEventListener('click', function() {
        const token = document.getElementById('item-token').value;
        api.validateToken(token, 'item');
    });
    
    document.getElementById('inject-items').addEventListener('click', function() {
        api.injectItems();
    });
    
    // API Tool Event Listeners
    document.getElementById('get-user-info').addEventListener('click', function() {
        api.getUserInfo();
    });
    
    document.getElementById('send-friend').addEventListener('click', function() {
        api.sendFriend();
    });
    
    document.getElementById('get-banner').addEventListener('click', function() {
        api.getBanner();
    });
    
    document.getElementById('send-likes').addEventListener('click', function() {
        api.sendLikes();
    });
    
    document.getElementById('get-outfit').addEventListener('click', function() {
        api.getOutfit();
    });
    
    // Modal Event Listeners
    document.querySelector('.close-modal').addEventListener('click', function() {
        document.getElementById('result-modal').style.display = 'none';
    });
    
    document.getElementById('result-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            this.style.display = 'none';
        }
    });
    
    // Smooth scrolling for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Add Enter key support for inputs
    document.querySelectorAll('.input-field').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const button = this.parentElement.querySelector('.btn');
                if (button) button.click();
            }
        });
    });
});