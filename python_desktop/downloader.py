import os
import yt_dlp

class YoutubeDownloader:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

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
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                }
            }
        }
        
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
            ydl.download([url])
