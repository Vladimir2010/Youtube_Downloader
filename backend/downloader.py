import os
import yt_dlp
from typing import Dict, List, Callable, Optional


class YoutubeDownloader:
    def __init__(self):
        self.progress_callback: Optional[Callable] = None
        self.download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(self.download_dir, exist_ok=True)

    def get_formats(self, url: str) -> Dict:
        """Extract video information and available formats."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract unique video resolutions
            video_formats = []
            seen_heights = set()
            
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('height'):
                    height = f['height']
                    if height not in seen_heights:
                        seen_heights.add(height)
                        video_formats.append({
                            'resolution': f"{height}p",
                            'height': height
                        })
            
            # Sort by resolution descending
            video_formats.sort(key=lambda x: x['height'], reverse=True)
            
            # Extract audio bitrates
            audio_formats = []
            seen_bitrates = set()
            
            for f in info.get('formats', []):
                if f.get('acodec') != 'none' and f.get('abr'):
                    abr = int(f['abr'])
                    if abr not in seen_bitrates:
                        seen_bitrates.add(abr)
                        audio_formats.append({
                            'bitrate': f"{abr}kbps",
                            'abr': abr
                        })
            
            audio_formats.sort(key=lambda x: x['abr'], reverse=True)
            
            return {
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'video_formats': [f['resolution'] for f in video_formats],
                'audio_formats': [f['bitrate'] for f in audio_formats]
            }

    def _progress_hook(self, d):
        """Progress callback for yt-dlp."""
        if d['status'] == 'downloading':
            if self.progress_callback:
                try:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        percent = (downloaded / total) * 100
                        self.progress_callback(percent)
                except:
                    pass

    def download(self, url: str, quality: str, mode: str) -> str:
        """
        Download video/audio from YouTube.
        
        Args:
            url: YouTube URL
            quality: Resolution (e.g., "1080p") or bitrate (e.g., "192kbps")
            mode: "video_only", "audio_only", or "video_audio"
        
        Returns:
            Path to downloaded file
        """
        ydl_opts = {
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        if mode == 'audio_only':
            # Extract audio only
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality.replace('kbps', ''),
            }]
        elif mode == 'video_only':
            # Video only (no audio)
            height = quality.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={height}]'
        else:  # video_audio
            # Best video + audio, merge with ffmpeg
            height = quality.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            ydl_opts['merge_output_format'] = 'mp4'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Handle audio conversion
            if mode == 'audio_only':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            return filename
