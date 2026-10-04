import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Cobalt Proxy (v9) is running!", 200

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

        # ใช้ Cobalt API แบบโครงสร้างมาตรฐานล่าสุด
        cobalt_url = "https://api.cobalt.tools/api/json"
        
        payload = {
            "url": youtube_url
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            res = requests.post(cobalt_url, json=payload, headers=headers, verify=False, timeout=10)
            if res.status_code == 200:
                res_data = res.json()
                status = res_data.get("status")
                
                if status in ["stream", "redirect", "picker"]:
                    audio_url = res_data.get("url")
                    title = res_data.get("filename", "Unknown Title")
                    
                    # กรณีเป็นแบบ picker (มีหลายความละเอียด/หลายไฟล์) ให้ดึงตัวแรกสุด
                    if not audio_url and "picker" in res_data and len(res_data["picker"]) > 0:
                        audio_url = res_data["picker"][0].get("url")
                else:
                    last_error = res_data.get("text", f"Cobalt status: {status}")
            else:
                last_error = f"API returned status {res.status_code}"
        except Exception as e:
            last_error = str(e)

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