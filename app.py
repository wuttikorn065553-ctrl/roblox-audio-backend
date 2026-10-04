import os
import requests
from flask import Flask, request, jsonify
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Multi-Invidious Audio Proxy is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']

        # ดึง Video ID ออกมาจากลิงก์
        video_id = None
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
        elif "embed/" in youtube_url:
            video_id = youtube_url.split("embed/")[1].split("?")[0]

        if not video_id:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400

        # รายชื่อ Invidious Instances สำรอง
        instances = [
            "https://vid.priv.au",
            "https://invidious.projectsegfau.lt",
            "https://iv.datura.network",
            "https://invidious.io.lol"
        ]

        audio_url = None
        title = "Unknown Title"
        last_error = ""

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        for instance in instances:
            try:
                res = requests.get(f"{instance}/api/v1/videos/{video_id}", headers=headers, verify=False, timeout=5)
                if res.status_code == 200:
                    res_data = res.json()
                    title = res_data.get('title', 'Unknown Title')
                    
                    # ค้นหาลิงก์เสียงจาก adaptiveFormats
                    adaptive_streams = res_data.get('adaptiveFormats', [])
                    for stream in adaptive_streams:
                        if 'audio' in stream.get('type', ''):
                            audio_url = stream.get('url')
                            break
                    
                    if audio_url:
                        break
                else:
                    last_error = f"Instance {instance} status {res.status_code}"
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