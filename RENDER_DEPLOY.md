# Render Deployment Guide

## 📦 Deploy Backend на Render

### 1. Подготовка на GitHub Repository

```bash
# Инициализирай Git (ако не си го направил)
cd c:\Users\Dell\PycharmProjects\Youtube
git init
git add .
git commit -m "Initial commit - YouTube Downloader Web + Backend"

# Създай GitHub repo и push-ни
git remote add origin https://github.com/<твоят-username>/youtube-downloader.git
git branch -M main
git push -u origin main
```

### 2. Deploy на Render.com

1. **Отиди на** [render.com](https://render.com) и влез с GitHub акаунт

2. **Създай нов Web Service**:
   - Кликни **New +** → **Web Service**
   - Избери твоя GitHub repository
   - Конфигурация:
     - **Name**: `youtube-downloader-backend`
     - **Region**: Frankfurt (EU Central)
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free

3. **Environment Variables** (не са задължителни за този проект)

4. **Deploy**:
   - Кликни **Create Web Service**
   - Изчакай 5-10 минути за deploy

5. **Вземи URL**:
   - След deploy ще получиш URL като: `https://youtube-downloader-backend.onrender.com`

---

## 🔧 Конфигуриране на APK

### Промени Backend URL във Frontend

Отвори `frontend/app.js` и промени:

```javascript
// Стара версия (localhost)
const API_BASE_URL = 'http://localhost:5000';

// Нова версия (Render)
const API_BASE_URL = 'https://youtube-downloader-backend.onrender.com';
```

### Sync Capacitor

```bash
npx cap sync
```

### Rebuild APK

1. Отвори Android Studio
2. Build → Build Bundle(s) / APK(s) → Build APK(s)
3. Новият APK ще работи с Render backend

---

## ⚠️ Важни бележки за Render

### 1. Free Tier Limitations
- **Sleep Mode**: След 15 минути неактивност, сървърът "заспива"
- **Първа заявка**: Може да отнеме 30-60 секунди за "събуждане"
- **Решение**: Използвай платен план ($7/месец) или UptimeRobot за ping

### 2. ffmpeg на Render
Render има ffmpeg предварително инсталиран, но ако има проблеми, добави `render.yaml`:

```yaml
services:
  - type: web
    name: youtube-downloader-backend
    env: python
    region: frankfurt
    buildCommand: |
      pip install -r requirements.txt
      apt-get update && apt-get install -y ffmpeg
    startCommand: gunicorn app:app
    plan: free
```

### 3. Disk Space
- Free tier има ограничено дисково пространство
- Свалените файлове се трият при рестарт
- За production: използвай cloud storage (AWS S3, Cloudinary)

---

## 🧪 Тестване

### Test Backend URL

```bash
curl https://youtube-downloader-backend.onrender.com/formats \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Test в браузър

1. Отвори `frontend/index.html`
2. Постави YouTube URL
3. Провери дали работи с Render backend

---

## 🚀 Алтернативи на Render

| Platform | Free Tier | ffmpeg | Deployment |
|----------|-----------|--------|------------|
| **Render** | ✅ 750h/месец | ✅ | GitHub Auto-deploy |
| **Railway** | ✅ $5 credit | ✅ | GitHub/CLI |
| **Fly.io** | ✅ Limited | ✅ | CLI |
| **Heroku** | ❌ (платен) | ✅ | GitHub/CLI |

---

## 📝 Quick Reference

**Render Backend URL Pattern:**
```
https://<service-name>.onrender.com
```

**Frontend Update:**
```javascript
const API_BASE_URL = 'https://<твоят-service>.onrender.com';
```

**Capacitor Sync:**
```bash
npx cap sync
npx cap open android
```
