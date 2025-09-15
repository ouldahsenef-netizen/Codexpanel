from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/validate-token', methods=['POST'])
def validate_token():
    """Validate access token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Access token is required'
            }), 400
            
        # Simple token validation (you can enhance this)
        if len(token) < 10:
            return jsonify({
                'success': False,
                'message': 'Invalid access token format'
            }), 401
            
        return jsonify({
            'success': True,
            'message': 'Access token is valid'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/update-bio', methods=['POST'])
def update_bio():
    """Update bio using the provided API"""
    try:
        data = request.get_json()
        access_token = data.get('accessToken', '').strip()
        new_bio = data.get('newBio', '').strip()
        
        if not access_token or not new_bio:
            return jsonify({
                'success': False,
                'message': 'Access token and bio content are required'
            }), 400
            
        # Make request to bio update API
        bio_url = f"https://change-bio-bngx.vercel.app/update_bio/{access_token}/{quote(new_bio)}"
        
        response = requests.post(bio_url, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Bio updated successfully',
                'data': response_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Bio update failed',
                'details': response_data
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/user-info/<uid>')
def get_user_info(uid):
    """Get user information"""
    try:
        if not uid.strip():
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
            
        # Make request to user info API
        info_url = f"https://info-me-ob50.vercel.app/get?uid={uid}"
        
        response = requests.get(info_url, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'User info retrieved successfully',
                'data': response_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve user info',
                'details': response_data
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/send-friend', methods=['POST'])
def send_friend():
    """Send friend request"""
    try:
        data = request.get_json()
        player_id = data.get('playerId', '').strip()
        
        if not player_id:
            return jsonify({
                'success': False,
                'message': 'Player ID is required'
            }), 400
            
        # Make request to friend spam API
        friend_url = f"https://spambngx.vercel.app/send_friend?player_id={player_id}"
        
        response = requests.post(friend_url, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Friend request sent successfully',
                'data': response_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Friend request failed',
                'details': response_data
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/banner/<uid>')
def get_banner(uid):
    """Get user banner"""
    try:
        if not uid.strip():
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
            
        key = request.args.get('key', 'BNGX')
        banner_url = f"https://bnrbngx-nu.vercel.app/bnr?uid={uid}&key={key}"
        
        response = requests.get(banner_url, timeout=30)
        
        if response.status_code == 200:
            # Check if response is JSON
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    response_data = response.json()
                    return jsonify({
                        'success': True,
                        'message': 'Banner retrieved successfully',
                        'data': response_data
                    })
                except:
                    pass
            
            # Handle direct image or encoded data response
            response_text = response.text.strip()
            
            # Check if it's an image URL
            if response_text.startswith('http') and ('image' in response_text or 'img' in response_text or 
                                                    response_text.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
                return jsonify({
                    'success': True,
                    'message': 'Banner image retrieved successfully',
                    'data': response_text
                })
            
            # If it's encoded image data (PNG signature detected) or other text
            if 'PNG' in response_text or len(response_text) > 100:
                return jsonify({
                    'success': True,
                    'message': 'Banner data retrieved successfully',
                    'data': response_text,
                    'type': 'encoded_data'
                })
            
            # Default case for short text responses
            return jsonify({
                'success': True,
                'message': 'Banner data retrieved successfully',
                'data': response_text
            })
        else:
            try:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
            except:
                response_data = {"message": response.text}
            return jsonify({
                'success': False,
                'message': 'Banner request failed',
                'details': response_data
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/send-likes', methods=['POST'])
def send_likes():
    """Send likes"""
    try:
        data = request.get_json()
        player_id = data.get('playerId', '').strip()
        
        if not player_id:
            return jsonify({
                'success': False,
                'message': 'Player ID is required'
            }), 400
            
        likes_url = f"https://likesbngx-rosy.vercel.app/send_like?player_id={player_id}"
        
        response = requests.post(likes_url, timeout=30)
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Likes sent successfully',
                'data': response_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Like request failed',
                'details': response_data
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/outfit/<uid>')
def get_outfit(uid):
    """Get user outfit"""
    try:
        if not uid.strip():
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
            
        region = request.args.get('region', 'me')
        key = request.args.get('key', 'BNGX')
        outfit_url = f"https://outfit-eta.vercel.app/api?region={region}&uid={uid}&key={key}"
        
        response = requests.get(outfit_url, timeout=30)
        
        if response.status_code == 200:
            # Check if response is JSON
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    response_data = response.json()
                    return jsonify({
                        'success': True,
                        'message': 'Outfit data retrieved successfully',
                        'data': response_data
                    })
                except:
                    pass
            
            # Handle direct image or encoded data response
            response_text = response.text.strip()
            
            # Check if it's an image URL
            if response_text.startswith('http') and ('image' in response_text or 'img' in response_text or 
                                                    response_text.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
                return jsonify({
                    'success': True,
                    'message': 'Outfit image retrieved successfully',
                    'data': response_text
                })
            
            # If it's encoded image data (PNG signature detected) or other text
            if 'PNG' in response_text or len(response_text) > 100:
                return jsonify({
                    'success': True,
                    'message': 'Outfit data retrieved successfully',
                    'data': response_text,
                    'type': 'encoded_data'
                })
            
            # Default case for short text responses
            return jsonify({
                'success': True,
                'message': 'Outfit data retrieved successfully',
                'data': response_text
            })
        else:
            try:
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"message": response.text}
            except:
                response_data = {"message": response.text}
            return jsonify({
                'success': False,
                'message': 'Outfit request failed',
                'details': response_data
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'message': f'API request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

@app.route('/api/add-items', methods=['POST'])
def add_items():
    """Add items (placeholder - API endpoint to be configured)"""
    try:
        data = request.get_json()
        access_token = data.get('accessToken', '').strip()
        item_id = data.get('itemId', '').strip()
        
        if not access_token or not item_id:
            return jsonify({
                'success': False,
                'message': 'Access token and item ID are required'
            }), 400
            
        # This endpoint will be configured later by admin
        return jsonify({
            'success': False,
            'message': 'Item addition API endpoint is not yet configured. Please contact the admin to set up the API endpoint.',
            'pendingConfiguration': True
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error occurred'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)