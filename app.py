import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Multi-Cobalt Proxy (v14) is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']
        audio_url = None
        title = "Unknown Title"
        last_error = ""

        # รายชื่อ Instance สำรองของ Cobalt และ API Gateway ทางเลือก
        endpoints = [
            "https://api.cobalt.tools/api/json",
            "https://co.wuk.sh/api/json"
        ]

        payload = {
            "url": youtube_url,
            "downloadMode": "audio"
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://cobalt.tools",
            "Referer": "https://cobalt.tools/"
        }

        for endpoint in endpoints:
            try:
                res = requests.post(endpoint, json=payload, headers=headers, verify=False, timeout=8)
                if res.status_code == 200:
                    res_data = res.json()
                    status = res_data.get("status")
                    
                    if status in ["stream", "redirect", "picker"]:
                        audio_url = res_data.get("url")
                        title = res_data.get("filename", "Unknown Title")
                        
                        if not audio_url and "picker" in res_data and len(res_data["picker"]) > 0:
                            audio_url = res_data["picker"][0].get("url")
                    else:
                        last_error = res_data.get("text", f"Status: {status}")
                        
                    if audio_url:
                        break
                else:
                    last_error = f"API returned status {res.status_code}"
            except Exception as e:
                last_error = str(e)
                continue

        if not audio_url:
            print(f"Extraction failed. Last error: {last_error}")
            return jsonify({'success': False, 'error': f'Failed: {last_error}'}), 500

        return jsonify({
            'success': True,
            'title': title,
            'audioUrl': audio_url
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)