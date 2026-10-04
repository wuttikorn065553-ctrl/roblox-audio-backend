import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Proxy (v5) is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']

        # ดึง Video ID เผื่อใช้กับ API สำรองตัวอื่น
        video_id = None
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[1].split("?")[0]

        audio_url = None
        title = "Unknown Title"
        last_error = ""

        # รายชื่อ Public APIs ทางเลือก
        apis = [
            f"https://apis.davidcyriltech.my.id/youtube/mp3?url={youtube_url}",
            f"https://api.siputzx.my.id/api/d/ytmp3?url={youtube_url}"
        ]

        for api_url in apis:
            try:
                res = requests.get(api_url, verify=False, timeout=8)
                if res.status_code == 200:
                    res_data = res.json()
                    
                    # ตรวจสอบโครงสร้างข้อมูลที่ส่งกลับมาจากแต่ละ API
                    if "data" in res_data and isinstance(res_data["data"], dict):
                        d = res_data["data"]
                        audio_url = d.get("download") or d.get("dl") or d.get("url")
                        title = d.get("title", "Unknown Title")
                    elif "result" in res_data and isinstance(res_data["result"], dict):
                        d = res_data["result"]
                        audio_url = d.get("download_url") or d.get("link") or d.get("url")
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