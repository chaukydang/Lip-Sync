# 🧠 Real-Time Lip-Sync WebSocket API (MuseTalk-ready)

This project provides a real-time lip-syncing API using **FastAPI** and **WebSocket**, allowing you to generate lip-synced video clips from a base64 image and audio input.

Built to be compatible with [MuseTalk](https://github.com/TMElyralab/MuseTalk), but comes with a working ffmpeg-based dummy backend that creates videos using a static image + audio.

---

## 🚀 Features

* 🎧 Accepts base64-encoded image and `.wav` audio
* ⟳ Returns generated video as base64 or direct URL
* 🌐 WebSocket endpoint (`/ws/lip-sync`)
* 🐳 Docker support included
* ✅ Compatible with MuseTalk integration

---

## 🗂 Project Structure

```
.
├── main.py               # FastAPI app with WebSocket
├── requirements.txt      # Python dependencies
├── Dockerfile            # Buildable docker image
├── static/videos/        # Output folder for videos
└── README.md             # You are here
```

---

## ⚙️ Requirements

* Python 3.10+
* ffmpeg (must be installed and in PATH)

### ✅ macOS:

```bash
brew install ffmpeg
```

### ✅ Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 🧪 Installation (Local)

### Step 1: Clone & Setup Virtual Environment

```bash
git clone <your-repo-url>
cd <project-folder>

python3.10 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Run the server

```bash
python main.py
```

You’ll see:

```
Uvicorn running on http://127.0.0.1:8000
```

---

## 🌐 WebSocket API

### 📍 Endpoint:

```
ws://localhost:8000/ws/lip-sync
```

### 📤 Input Message Format (JSON):

```json
{
  "audio": "<base64-wav-data>",
  "image": "<base64-image-data>",
  "output_format": "base64"  // or "url"
}
```

### 📥 Output Response:

#### ✅ On success:

```json
{
  "status": "success",
  "video_base64": "<mp4-base64>"     // if output_format == "base64"
}
```

or

```json
{
  "status": "success",
  "video_url": "/static/videos/output_xyz.mp4"  // if output_format == "url"
}
```

#### ❌ On error:

```json
{
  "status": "error",
  "message": "Missing required fields: 'audio' and 'image'"
}
```

---

## 🔄 Test Using Postman

1. Connect to: `ws://localhost:8000/ws/lip-sync`
2. Send JSON message with base64 fields
3. Receive base64 video or URL response
4. Optional: decode base64 to `.mp4` using:

```bash
echo "<base64 string>" | base64 -d > output.mp4
```

---

## 🐳 Run with Docker

### Step 1: Build the image

```bash
docker build -t lipsync-api .
```

### Step 2: Run the container

```bash
docker run -p 8000:8000 lipsync-api
```

---

## 🧠 MuseTalk Integration (Optional)

To replace the dummy ffmpeg backend with MuseTalk:

* Update `generate_video()` in `LipSyncAPI` to call your MuseTalk inference code
* Replace `create_demo_video()` with `musetalk/inference.py` or `LipSyncModel`

---

## ✅ Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

## 📜 License

MIT or other (depending on your usage). MuseTalk is under its own license.

---