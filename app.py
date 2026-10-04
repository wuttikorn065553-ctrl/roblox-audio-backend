import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Proxy (v4) is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']

        # ใช้บริการ API สำรองที่รองรับการดึงลิงก์ผ่านคลาวด์โดยตรง
        api_endpoints = [
            f"https://co.wuk.sh/api/json" # ถ้าตัวนี้ยังเปิด หรือเปลี่ยนเป็นตัวอื่น
        ]
        
        # เนื่องจาก Public API มักจะปิดตัวไว เราจะใช้การดึงผ่าน y2mate/loader ทางเลือก หรือใช้บริการ api สาธารณะที่ปลอดภัย
        # เปลี่ยนมาใช้บริการผ่าน proxy ของสตรีมเพลงที่มีเสถียรภาพสูงแทน
        alt_api = "https://apis.davidcyriltech.my.id/youtube/mp3?url="

        audio_url = None
        title = "Unknown Title"
        last_error = ""

        try:
            res = requests.get(f"{alt_api}{youtube_url}", verify=False, timeout=8)
            if res.status_code == 200:
                res_data = res.json()
                if res_data.get("status") == 200 or "success" in str(res_data).lower():
                    # ดึงลิงก์ดาวน์โหลดเสียงจากโครงสร้างผลลัพธ์
                    data_obj = res_data.get("result", {})
                    audio_url = data_obj.get("download_url") or data_obj.get("link")
                    title = data_obj.get("title", "Unknown Title")
                else:
                    last_error = f"API response format error: {res_data}"
            else:
                last_error = f"Alternative API returned status {res.status_code}"
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