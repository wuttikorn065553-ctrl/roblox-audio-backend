import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Invidious Proxy is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']
        
        # แยกดึง Video ID ออกมาจากลิงก์ YouTube
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
        else:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400

        # รายชื่อ Invidious Public Instances สำรอง
        invidious_instances = [
            "https://invidious.privacyredirect.com",
            "https://vid.puffyan.us",
            "https://inv.nadeko.net"
        ]

        audio_url = None
        title = "Unknown Title"

        for instance in invidious_instances:
            try:
                res = requests.get(f"{instance}/api/v1/videos/{video_id}", timeout=5)
                if res.status_code == 200:
                    vid_data = res.json()
                    title = vid_data.get('title', 'Unknown Title')
                    adaptive_formats = vid_data.get('adaptiveFormats', [])
                    
                    # ค้นหาลิงก์สตรีมเสียงที่ดีที่สุด
                    for f in adaptive_formats:
                        if 'audio' in f.get('type', ''):
                            audio_url = f.get('url')
                            break
                    if audio_url:
                        break
            except Exception:
                continue

        if not audio_url:
            return jsonify({'success': False, 'error': 'Could not extract audio stream'}), 500

        return jsonify({
            'success': True,
            'title': title,
            'audioUrl': audio_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)