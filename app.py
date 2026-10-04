import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Roblox Audio Backend (Cookies Auth) is running!", 200

@app.route('/get-audio', methods=['POST'])
def get_audio():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'Missing youtube url'}), 400

        youtube_url = data['url']

        # เช็คว่ามีไฟล์ cookies.txt อยู่ไหม
        cookie_file = 'cookies.txt'
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'tv', 'web']
                }
            }
        }

        if os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(youtube_url, download=False)
            except Exception as e:
                return jsonify({'success': False, 'error': f'yt-dlp error: {str(e)}'}), 500

            title = info.get('title', 'Unknown Title')
            audio_url = info.get('url')

            if not audio_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_url = f.get('url')
                        break

            if not audio_url:
                return jsonify({'success': False, 'error': 'Could not extract audio stream URL'}), 500

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