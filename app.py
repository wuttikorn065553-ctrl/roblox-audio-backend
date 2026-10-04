import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Cobalt Proxy is running!", 200

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

        # ใช้บริการ Cobalt Public API สำหรับดึงลิงก์ตรง
        cobalt_apis = [
            "https://api.cobalt.tools/api/json"
        ]

        payload = {
            "url": youtube_url,
            "downloadMode": "audio",
            "audioFormat": "mp3"
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        for api_url in cobalt_apis:
            try:
                res = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                if res.status_code == 200:
                    res_data = res.json()
                    # โครงสร้างของ Cobalt API
                    status = res_data.get("status")
                    if status == "stream" or status == "redirect" or status == "picker":
                        audio_url = res_data.get("url")
                        title = res_data.get("filename", "Unknown Title")
                        break
                    elif status == "error":
                        last_error = res_data.get("text", "Cobalt error")
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