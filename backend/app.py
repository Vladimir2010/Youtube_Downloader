from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from downloader import YoutubeDownloader
import os
import threading
import uuid
from typing import Dict

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global storage for download sessions
download_sessions: Dict[str, Dict] = {}
downloader = YoutubeDownloader()


@app.route('/formats', methods=['POST'])
def get_formats():
    """Extract available formats for a YouTube URL."""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        formats = downloader.get_formats(url)
        return jsonify(formats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['POST'])
def start_download():
    """Start a download job."""
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality')
        mode = data.get('mode', 'video_audio')
        
        if not url or not quality:
            return jsonify({'error': 'URL and quality are required'}), 400
        
        # Create session ID
        session_id = str(uuid.uuid4())
        download_sessions[session_id] = {
            'status': 'starting',
            'progress': 0,
            'file_path': None,
            'error': None
        }
        
        # Define progress callback
        def update_progress(percent):
            download_sessions[session_id]['progress'] = percent
            download_sessions[session_id]['status'] = 'downloading'
        
        # Start download in background thread
        def download_task():
            try:
                downloader.progress_callback = update_progress
                file_path = downloader.download(url, quality, mode)
                download_sessions[session_id]['status'] = 'completed'
                download_sessions[session_id]['progress'] = 100
                download_sessions[session_id]['file_path'] = file_path
            except Exception as e:
                download_sessions[session_id]['status'] = 'error'
                download_sessions[session_id]['error'] = str(e)
        
        thread = threading.Thread(target=download_task)
        thread.start()
        
        return jsonify({'session_id': session_id}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status/<session_id>', methods=['GET'])
def get_status(session_id):
    """Get download status for a session."""
    session = download_sessions.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    response = {
        'status': session['status'],
        'progress': session['progress']
    }
    
    if session['status'] == 'error':
        response['error'] = session['error']
    elif session['status'] == 'completed':
        response['filename'] = os.path.basename(session['file_path'])
    
    return jsonify(response), 200


@app.route('/file/<session_id>', methods=['GET'])
def download_file(session_id):
    """Download the completed file."""
    session = download_sessions.get(session_id)
    
    if not session or session['status'] != 'completed':
        return jsonify({'error': 'File not ready'}), 404
    
    file_path = session['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )


if __name__ == '__main__':
    print("🚀 YouTube Downloader Backend starting...")
    print("📡 Server running on http://localhost:5000")
    print("📋 Endpoints:")
    print("   POST /formats - Get available formats")
    print("   POST /download - Start download")
    print("   GET  /status/<session_id> - Check progress")
    print("   GET  /file/<session_id> - Download file")
    app.run(debug=True, host='0.0.0.0', port=5000)
