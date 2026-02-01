import os
import sys
import yt_dlp

class YoutubeDownloader:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        """Locates ffmpeg.exe in several potential locations."""
        locations = []
        
        # 1. If running as a bundled executable
        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            # PyInstaller 6.x puts things in _internal in one-dir mode
            internal_dir = os.path.join(base_dir, '_internal')
            
            locations.extend([
                os.path.join(base_dir, 'bin', 'ffmpeg.exe'),
                os.path.join(internal_dir, 'bin', 'ffmpeg.exe'),
                os.path.join(base_dir, 'ffmpeg.exe'),
                os.path.join(internal_dir, 'ffmpeg.exe'),
            ])
        
        # 2. Development paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        locations.extend([
            os.path.join(script_dir, 'bin', 'ffmpeg.exe'),
            os.path.join(script_dir, 'ffmpeg.exe'),
        ])
        
        # Check all possible locations
        for loc in locations:
            if os.path.exists(loc):
                return loc
            
        # 3. Fallback to PATH
        return 'ffmpeg'

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '')
            try:
                percent = float(p)
                if self.progress_callback:
                    self.progress_callback(percent)
            except ValueError:
                pass

    def get_info(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': self.ffmpeg_path,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                }
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                resolutions = set()
                audio_bitrates = set()

                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('height'):
                        resolutions.add(f['height'])
                    
                    if f.get('acodec') != 'none' and f.get('abr'):
                        audio_bitrates.add(int(f['abr']))
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'resolutions': sorted(list(resolutions), reverse=True),
                    'audio_bitrates': sorted(list(audio_bitrates), reverse=True),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail')
                }
            except Exception as e:
                raise Exception(f"Error fetching info: {str(e)}")

    def download(self, url, save_path, resolution='720', mode='video_audio'):
        common_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'ffmpeg_location': self.ffmpeg_path,
            'nocheckcertificate': True,
            'windowsfilenames': True,
            'overwrites': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                }
            }
        }
        
        # ... (rest of mode logic stays same)
        if mode == 'audio_only':
            bitrate = resolution if resolution else '192' 
            ydl_opts = {
                **common_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': str(bitrate),
                }],
            }
        elif mode == 'video_only':
            ydl_opts = {
                **common_opts,
                'format': f'bestvideo[height<={resolution}]/best',
            }
        else:
            ydl_opts = {
                **common_opts,
                'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # If it was an audio download, the extension changed to .mp3
            if mode == 'audio_only':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            # Check if file exists and has size > 0
            if not os.path.exists(filename):
                # Try to find the file if the title substitution changed something
                # This is fallback logic
                pass
            elif os.path.getsize(filename) == 0:
                raise Exception("Сваленият файл е празен. Вероятно проблем с YouTube или интернет връзката.")
