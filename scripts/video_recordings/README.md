# Video Capture Script – `videoscript.sh`

This folder contains the script used to capture short video clips from a Hikvision camera using RTSP, store them locally (SSD or fallback RAM), and upload them to MinIO object storage.

---

## ⚙️ Configuration

The script reads all sensitive or variable settings from a `.env` file stored in the same folder.

### 📄 `.env` file

This file **is not committed to GitHub**. Instead, use the provided `.env.example` to create your own:

```bash
cp .env.example .env

