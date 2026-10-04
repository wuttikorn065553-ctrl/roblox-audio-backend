import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox YouTube Audio Proxy is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']

        # ตั้งค่า yt-dlp พร้อมดึงไฟล์คุกกี้เพื่อเลี่ยงการบล็อกบนคลาวด์
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'youtube.com_cookies.txt',  # ไฟล์คุกกี้ที่เรานำมาใส่ไว้
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web']
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            audio_url = info.get('url')
            title = info.get('title', 'Unknown Title')

        if not audio_url:
            return jsonify({'success': False, 'error': 'Could not extract audio stream'}), 500

        return jsonify({
            'success': True,
            'title': title,
            'audioUrl': audio_url
        })

    except Exception as e:
        error_msg = str(e)
        print(f"Detailed Error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)