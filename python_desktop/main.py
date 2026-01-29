import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QComboBox, 
                             QRadioButton, QButtonGroup, QLabel, QFileDialog, 
                             QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from downloader import YoutubeDownloader

import requests
from PySide6.QtGui import QPixmap, QImage, QIcon

class DownloadThread(QThread):
    progress = Signal(float)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, downloader, url, save_path, resolution, mode):
        super().__init__()
        self.downloader = downloader
        self.url = url
        self.save_path = save_path
        self.resolution = resolution
        self.mode = mode
        self.downloader.progress_callback = self.update_progress

    def update_progress(self, p):
        self.progress.emit(p)

    def run(self):
        try:
            self.downloader.download(self.url, self.save_path, self.resolution, self.mode)
            self.finished.emit("Download completed successfully!")
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader Pro (Desktop)")
        # Define path based on execution mode (Frozen/Dev)
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(base_path, "app_icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumWidth(600)
        self.downloader = YoutubeDownloader()
        self.save_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        self.current_resolutions = []
        self.current_bitrates = []
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("🚀 YouTube Downloader")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        url_layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("Extract Info")
        self.fetch_btn.clicked.connect(self.fetch_metadata)
        url_layout.addWidget(self.fetch_btn)
        layout.addLayout(url_layout)

        self.info_layout = QHBoxLayout()
        
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(320, 180)
        self.thumb_label.setStyleSheet("background-color: #eee; border: 1px solid #ccc;")
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("No Preview")
        self.info_layout.addWidget(self.thumb_label)

        self.video_title = QLabel("Waiting for URL...")
        self.video_title.setWordWrap(True)
        self.video_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.info_layout.addWidget(self.video_title)
        
        layout.addLayout(self.info_layout)

        self.options_group = QWidget()
        options_layout = QVBoxLayout(self.options_group)
        
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup()
        
        self.radio_both = QRadioButton("Video + Audio (MP4)")
        self.radio_both.setChecked(True)
        self.radio_video = QRadioButton("Video Only")
        self.radio_audio = QRadioButton("Audio Only (MP3)")
        
        self.mode_group.addButton(self.radio_both)
        self.mode_group.addButton(self.radio_video)
        self.mode_group.addButton(self.radio_audio)
        
        self.mode_group.buttonToggled.connect(self.update_dropdown_options)
        
        mode_layout.addWidget(self.radio_both)
        mode_layout.addWidget(self.radio_video)
        mode_layout.addWidget(self.radio_audio)
        options_layout.addLayout(mode_layout)

        res_layout = QHBoxLayout()
        self.quality_label = QLabel("Quality:")
        res_layout.addWidget(self.quality_label)
        self.res_combo = QComboBox()
        res_layout.addWidget(self.res_combo)
        options_layout.addLayout(res_layout)

        layout.addWidget(self.options_group)

        path_layout = QHBoxLayout()
        self.path_label = QLabel(f"Save to: {self.save_directory}")
        self.path_label.setStyleSheet("color: #666;")
        path_layout.addWidget(self.path_label)
        
        path_btn = QPushButton("Change Folder")
        path_btn.clicked.connect(self.change_folder)
        path_layout.addWidget(path_btn)
        layout.addLayout(path_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        self.download_btn = QPushButton("Download Now")
        self.download_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def fetch_metadata(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        self.status_label.setText("Fetching video metadata...")
        self.fetch_btn.setEnabled(False)
        QApplication.processEvents()

        try:
            info = self.downloader.get_info(url)
            self.video_title.setText(info['title'])
            self.status_label.setText(f"Loaded: {info['title']}")
            
            if info['thumbnail']:
                try:
                    data = requests.get(info['thumbnail']).content
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    self.thumb_label.setPixmap(pixmap.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                except:
                    self.thumb_label.setText("No Preview")

            self.current_resolutions = info.get('resolutions', [])
            self.current_bitrates = info.get('audio_bitrates', [])
            
            self.update_dropdown_options()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText("Failed to fetch info")
        finally:
            self.fetch_btn.setEnabled(True)

    def update_dropdown_options(self):
        self.res_combo.clear()
        
        if self.radio_audio.isChecked():
            self.quality_label.setText("Audio Quality:")
            if self.current_bitrates:
                self.res_combo.addItems([str(b) for b in self.current_bitrates])
            else:
                self.res_combo.addItems(["192", "128", "256", "320"])
        else:
            self.quality_label.setText("Video Resolution:")
            if self.current_resolutions:
                self.res_combo.addItems([str(r) for r in self.current_resolutions])
            else:
                self.res_combo.addItems(["1080", "720", "480", "360", "240", "144"])

    def change_folder(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.save_directory)
        if dir:
            self.save_directory = dir
            self.path_label.setText(f"Save to: {self.save_directory}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return

        selection = self.res_combo.currentText()
        mode = 'video_audio'
        if self.radio_video.isChecked(): mode = 'video_only'
        if self.radio_audio.isChecked(): mode = 'audio_only'

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.download_btn.setEnabled(False)
        self.status_label.setText("Downloading...")

        self.thread = DownloadThread(self.downloader, url, self.save_directory, selection, mode)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_finished(self, msg):
        self.download_btn.setEnabled(True)
        self.status_label.setText("Complete!")
        QMessageBox.information(self, "Success", msg)
        self.progress_bar.setVisible(False)

    def on_error(self, err):
        self.download_btn.setEnabled(True)
        self.status_label.setText("Error occurred")
        QMessageBox.critical(self, "Error", err)
        self.progress_bar.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
