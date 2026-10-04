import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Proxy (Stable v10) is running!", 200

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

        # ใช้บริการดึงลิงก์ผ่าน API สาธารณะที่อัปเดตสตรีมตรง
        api_endpoints = [
            f"https://deliriussapi-oficial.vercel.app/download/ytmp3?url={youtube_url}",
            f"https://api.siputzx.my.id/api/d/ytmp3?url={youtube_url}"
        ]

        for api_url in api_endpoints:
            try:
                res = requests.get(api_url, verify=False, timeout=8)
                if res.status_code == 200 and "application/json" in res.headers.get("Content-Type", ""):
                    res_data = res.json()
                    
                    # แกะโครงสร้างข้อมูลตามรูปแบบมาตรฐาน
                    d = res_data.get("data") or res_data.get("result") or res_data
                    if isinstance(d, dict):
                        audio_url = d.get("download") or d.get("dl") or d.get("url") or d.get("download_url")
                        title = d.get("title", "Unknown Title")
                        
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