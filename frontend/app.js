// Configuration
const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const urlInput = document.getElementById('urlInput');
const fetchBtn = document.getElementById('fetchBtn');
const videoInfo = document.getElementById('videoInfo');
const thumbnail = document.getElementById('thumbnail');
const videoTitle = document.getElementById('videoTitle');
const videoDuration = document.getElementById('videoDuration');
const downloadOptions = document.getElementById('downloadOptions');
const qualitySelect = document.getElementById('qualitySelect');
const qualityLabel = document.getElementById('qualityLabel');
const downloadBtn = document.getElementById('downloadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const statusMessage = document.getElementById('statusMessage');

// State
let currentFormats = null;
let currentSessionId = null;

// Event Listeners
fetchBtn.addEventListener('click', fetchVideoInfo);
downloadBtn.addEventListener('click', startDownload);

// Listen for mode changes
document.querySelectorAll('input[name="mode"]').forEach(radio => {
    radio.addEventListener('change', updateQualityOptions);
});

// Fetch Video Info
async function fetchVideoInfo() {
    const url = urlInput.value.trim();

    if (!url) {
        showStatus('Моля, въведи YouTube URL', 'error');
        return;
    }

    fetchBtn.disabled = true;
    fetchBtn.textContent = 'Зареждане...';
    hideStatus();

    try {
        const response = await fetch(`${API_BASE_URL}/formats`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch formats');
        }

        const data = await response.json();
        currentFormats = data;

        // Display video info
        videoTitle.textContent = data.title;
        thumbnail.src = data.thumbnail || '';

        if (data.duration) {
            const minutes = Math.floor(data.duration / 60);
            const seconds = data.duration % 60;
            videoDuration.textContent = `Продължителност: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }

        videoInfo.classList.remove('hidden');
        downloadOptions.classList.remove('hidden');

        updateQualityOptions();

    } catch (error) {
        showStatus(`Грешка: ${error.message}`, 'error');
    } finally {
        fetchBtn.disabled = false;
        fetchBtn.textContent = 'Извлечи Инфо';
    }
}

// Update Quality Options based on mode
function updateQualityOptions() {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    qualitySelect.innerHTML = '<option value="">Избери качество</option>';

    if (!currentFormats) return;

    if (mode === 'audio_only') {
        qualityLabel.textContent = 'Аудио Качество:';
        currentFormats.audio_formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format;
            option.textContent = format;
            qualitySelect.appendChild(option);
        });
    } else {
        qualityLabel.textContent = 'Видео Резолюция:';
        currentFormats.video_formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format;
            option.textContent = format;
            qualitySelect.appendChild(option);
        });
    }
}

// Start Download
async function startDownload() {
    const url = urlInput.value.trim();
    const quality = qualitySelect.value;
    const mode = document.querySelector('input[name="mode"]:checked').value;

    if (!quality) {
        showStatus('Моля, избери качество', 'error');
        return;
    }

    downloadBtn.disabled = true;
    downloadBtn.textContent = 'Стартиране...';
    hideStatus();

    try {
        const response = await fetch(`${API_BASE_URL}/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, quality, mode })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start download');
        }

        const data = await response.json();
        currentSessionId = data.session_id;

        // Show progress bar
        progressContainer.classList.remove('hidden');

        // Start polling for status
        pollDownloadStatus();

    } catch (error) {
        showStatus(`Грешка: ${error.message}`, 'error');
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Свали Сега';
    }
}

// Poll Download Status
async function pollDownloadStatus() {
    if (!currentSessionId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/status/${currentSessionId}`);

        if (!response.ok) {
            throw new Error('Failed to get status');
        }

        const data = await response.json();

        // Update progress
        progressFill.style.width = `${data.progress}%`;
        progressText.textContent = `${Math.round(data.progress)}%`;

        if (data.status === 'completed') {
            showStatus('Свалянето завърши! Започва изтегляне...', 'success');
            downloadFile();
        } else if (data.status === 'error') {
            showStatus(`Грешка: ${data.error}`, 'error');
            resetDownloadUI();
        } else {
            // Continue polling
            setTimeout(pollDownloadStatus, 500);
        }

    } catch (error) {
        showStatus(`Грешка: ${error.message}`, 'error');
        resetDownloadUI();
    }
}

// Download File
function downloadFile() {
    const downloadUrl = `${API_BASE_URL}/file/${currentSessionId}`;

    // Create temporary link and trigger download
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    setTimeout(() => {
        resetDownloadUI();
        showStatus('Файлът е изтеглен успешно!', 'success');
    }, 1000);
}

// Reset Download UI
function resetDownloadUI() {
    downloadBtn.disabled = false;
    downloadBtn.textContent = 'Свали Сега';
    progressContainer.classList.add('hidden');
    progressFill.style.width = '0%';
    progressText.textContent = '0%';
    currentSessionId = null;
}

// Show Status Message
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
}

// Hide Status Message
function hideStatus() {
    statusMessage.style.display = 'none';
}

// Format seconds to MM:SS
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}
