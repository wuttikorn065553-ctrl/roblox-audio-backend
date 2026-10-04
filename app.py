import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Cobalt Audio Proxy is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']

        # ใช้ Cobalt API ในการดึงลิงก์สตรีมเสียง (เสถียรและไม่โดนบล็อกง่ายบนคลาวด์)
        cobalt_instances = [
            "https://co.wuk.sh/api/json",
            "https://cobalt.api.red,stone.cx",
            "https://api.cobalt.best"
        ]

        audio_url = None
        title = "Unknown Title"
        last_error = ""

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": youtube_url,
            "downloadMode": "audio",
            "audioFormat": "mp3"
        }

        for instance in cobalt_instances:
            try:
                res = requests.post(instance, json=payload, headers=headers, timeout=6)
                if res.status_code == 200:
                    res_data = res.json()
                    if res_data.get("status") in ["stream", "redirect", "success"]:
                        audio_url = res_data.get("url")
                        break
                    elif "text" in res_data:
                        audio_url = res_data.get("text") # บางกรณี cobalt ส่งมาเป็นลิงก์ตรงในฟิลด์ text
                        break
                else:
                    last_error = f"Cobalt returned status {res.status_code}"
            except Exception as e:
                last_error = str(e)
                continue

        if not audio_url:
            print(f"Cobalt extraction failed. Last error: {last_error}")
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