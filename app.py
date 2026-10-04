import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods('/', methods=['GET']) # type: ignore
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

        # ใช้ Endpoint หลักของ Cobalt ที่ยังใช้งานได้
        cobalt_url = "https://api.cobalt.best/"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        payload = {
            "url": youtube_url,
            "downloadMode": "audio",
            "audioFormat": "mp3"
        }

        audio_url = None
        title = "Unknown Title"
        last_error = ""

        try:
            res = requests.post(cobalt_url, json=payload, headers=headers, verify=False, timeout=8)
            if res.status_code == 200:
                try:
                    res_data = res.json()
                except Exception:
                    last_error = f"Non-JSON response: {res.text[:100]}"
                    raise Exception(last_error)

                status = res_data.get("status")
                if status in ["stream", "redirect", "success"]:
                    audio_url = res_data.get("url")
                elif "text" in res_data:
                    audio_url = res_data.get("text")
                else:
                    last_error = f"Cobalt status: {status}, data: {res_data}"
            else:
                last_error = f"Cobalt returned status {res.status_code}: {res.text[:100]}"
        except Exception as e:
            last_error = str(e)

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