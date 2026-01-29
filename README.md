# YouTube Downloader - Web + Backend Architecture

Този проект представя YouTube Downloader с модерна Web + Backend архитектура, подходяща за браузър и Android (чрез Capacitor).

---

## 🏗️ Архитектура

```
┌─────────────────┐
│  Web Browser /  │
│  Android WebView│
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask Backend  │
│   (Python)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────┐
│ yt-dlp │ │ffmpeg│
└────────┘ └──────┘
```

---

## 📁 Структура на проекта

```
Youtube/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── downloader.py       # yt-dlp wrapper
│   ├── requirements.txt
│   └── downloads/          # Temporary files
├── frontend/
│   ├── index.html          # Web UI
│   ├── style.css           # Responsive CSS
│   └── app.js              # Fetch API logic
├── android/                # Capacitor Android (generated)
├── capacitor.config.json
├── package.json
└── README.md
```

---

## 🚀 Backend (Flask + yt-dlp)

### Инсталация

```bash
cd backend
pip install -r requirements.txt
```

**Зависимости:**
- Flask 3.1.0
- Flask-CORS 5.0.0
- yt-dlp (latest)
- ffmpeg (системна инсталация)

### Стартиране

```bash
python app.py
```

Сървърът стартира на `http://localhost:5000`

### API Endpoints

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/formats` | POST | Извлича налични формати за YouTube URL |
| `/download` | POST | Стартира сваляне и връща session ID |
| `/status/<session_id>` | GET | Проверява прогреса на свалянето |
| `/file/<session_id>` | GET | Изтегля готовия файл |

**Пример заявка:**

```bash
# Get formats
curl -X POST http://localhost:5000/formats \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=..."}'

# Start download
curl -X POST http://localhost:5000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "quality": "1080p", "mode": "video_audio"}'
```

---

## 🌐 Frontend (Vanilla Web)

### Стартиране

Отвори `frontend/index.html` директно в браузър или използвай HTTP сървър:

```bash
cd frontend
python -m http.server 8080
```

Отвори: `http://localhost:8080`

### Функционалности

- ✅ Responsive дизайн (Mobile-first)
- ✅ Dark theme
- ✅ Real-time progress tracking
- ✅ Thumbnail preview
- ✅ Quality selection (Video/Audio)
- ✅ Download modes:
  - Video + Audio (MP4)
  - Video Only
  - Audio Only (MP3)

---

## 📱 Android APK (Capacitor)

### Предварителни изисквания

- Node.js 18+
- Android Studio
- Java JDK 17+

### Стъпки за генериране на APK

#### 1. Инсталирай Capacitor

```bash
npm install
```

#### 2. Инициализирай Capacitor (само първи път)

```bash
npx cap init
```

#### 3. Добави Android платформа

```bash
npx cap add android
```

#### 4. Синхронизирай файловете

```bash
npx cap sync
```

#### 5. Отвори в Android Studio

```bash
npx cap open android
```

#### 6. Build APK

В Android Studio:
1. **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Изчакай компилацията
3. APK файлът ще се намери в:
   ```
   android/app/build/outputs/apk/debug/app-debug.apk
   ```

### Важни настройки

**Backend URL за Android Emulator:**
- В `capacitor.config.json` е зададен `http://10.0.2.2:5000`
- `10.0.2.2` е специален IP адрес, който Android Emulator използва за достъп до `localhost` на хост машината

**За реално устройство:**
- Промени URL-а в `frontend/app.js`:
  ```javascript
  const API_BASE_URL = 'http://<твоя-локален-IP>:5000';
  ```
- Пример: `http://192.168.1.100:5000`

---

## 🧪 Тестване

### Backend Test

```bash
cd backend
python app.py
# В друг терминал:
curl http://localhost:5000/formats -X POST -H "Content-Type: application/json" -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Frontend Test

1. Стартирай backend
2. Отвори `frontend/index.html`
3. Постави YouTube URL
4. Тествай сваляне

---

## 📊 Сравнение: Desktop vs Web

| Характеристика | Desktop (PySide6) | Web + Backend |
|----------------|-------------------|---------------|
| **UI Framework** | Qt (PySide6) | HTML/CSS/JS |
| **Backend** | Вграден | Flask REST API |
| **Портативност** | Windows EXE | Browser + Android APK |
| **Deployment** | Inno Setup | Web hosting + Capacitor |
| **Сложност** | Ниска | Средна |

---

## ⚠️ Важни бележки

1. **Само за образователни цели** - Проектът е създаден за учебна защита
2. **ffmpeg изискване** - Трябва да е инсталиран системно за muxing
3. **CORS** - Backend има активиран CORS за cross-origin заявки
4. **Временни файлове** - Свалените файлове се съхраняват в `backend/downloads/`
5. **Production** - За production deployment използвай WSGI сървър (Gunicorn/uWSGI)

---

## 🎓 Учебна защита

Проектът демонстрира:
- REST API дизайн
- Асинхронна комуникация (Fetch API)
- Progress tracking с polling
- WebView интеграция (Capacitor)
- Cross-platform deployment (Web + Android)
- Модулна архитектура (Backend/Frontend separation)

---

## 📝 Лиценз

MIT License - Само за образователни цели
