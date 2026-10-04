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

        # ตั้งค่า yt-dlp ให้รองรับการดึงข้อมูลที่เสถียรขึ้น
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
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
        # พิมพ์ Error ลงใน Console ของ Render เพื่อให้เราเช็คได้ง่ายขึ้น
        print(f"Error extracting audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)