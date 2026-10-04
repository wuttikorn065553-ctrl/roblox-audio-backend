import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Proxy (v11) is running!", 200

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

        # ใช้ Endpoint ทางเลือกที่รองรับการแปลงและดึงสตรีมล่าสุด
        api_endpoints = [
            f"https://api.siputzx.my.id/api/d/ytmp3?url={youtube_url}"
        ]

        for api_url in api_endpoints:
            try:
                res = requests.get(api_url, verify=False, timeout=8)
                if res.status_code == 200:
                    # บางครั้ง API คืนค่าเป็นข้อความธรรมดาหรือ JSON ที่มีปัญหา ให้ลองเช็ค text ดูก่อน
                    if "application/json" in res.headers.get("Content-Type", ""):
                        res_data = res.json()
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

        # กรณีถ้า API หลักพลาด เราจะใช้ fallback สำรองแบบดึงสตรีมตรงผ่าน invidious สาธารณะที่ยังเปิดอยู่
        if not audio_url:
            try:
                video_id = None
                if "v=" in youtube_url:
                    video_id = youtube_url.split("v=")[1].split("&")[0]
                elif "youtu.be/" in youtube_url:
                    video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                
                if video_id:
                    inv_res = requests.get(f"https://invidious.projectsegfau.lt/api/v1/videos/{video_id}", timeout=5)
                    if inv_res.status_code == 200:
                        inv_data = inv_res.json()
                        title = inv_data.get('title', 'Unknown Title')
                        for stream in inv_data.get('adaptiveFormats', []):
                            if 'audio' in stream.get('type', ''):
                                audio_url = stream.get('url')
                                break
            except Exception as ex:
                last_error = f"Fallback error: {str(ex)}"

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