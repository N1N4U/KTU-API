<div align="center">

# 🎓 KTU API

**Lightweight Flask API that scrapes KTU student data such as grades, personal details, and more from the official KTU website and returns structured JSON**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Web Interface](#-web-interface) • [Configuration](#-configuration)

</div>

---

## ✨ Features

- 🔐 **Secure Authentication** — POST credentials to `/api/student` and receive structured JSON data
- 🎨 **Modern Web UI** — Built-in dark-themed testing interface at `/` 
- 📊 **Structured Logging** — Color-coded console logs with configurable verbosity
- ⚙️ **Environment Config** — `.env` support for `SERVER_PORT` and `LOG_LEVEL`
- 📱 **Responsive Design** — Mobile-friendly interface (16:9 desktop, stacked mobile)
- 💾 **JSON Export** — Download scraped data directly from the web interface

---

## 🚀 Quick Start

### 1. Clone & Navigate
```bash
git clone "https://github.com/N1N4U/KTU-API"
cd "KTU API"
```

### 2. (Optional) Create Virtual Environment
**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root:
```env
SERVER_PORT=5000
LOG_LEVEL=INFO
```

> **Note:** A sample `.env` is already included. Update `SERVER_PORT` if needed.

### 5. Run the Application
```bash
py app.py
```

The server will start on `http://localhost:5000`

---

## 🌐 Web Interface

Access the modern web UI at **http://localhost:5000/** 

### Features:
- 🎯 **Dark Theme** — Green accent colors optimized for readability
- 📋 **Side-by-Side View** — Details on left, JSON code block on right (desktop)
- 📱 **Mobile Responsive** — Code block on top, details below (mobile)
- ⬇️ **JSON Download** — One-click download button in code header
- ⚠️ **Error Handling** — Clear error messages for login failures and API issues

---

## 📡 API Documentation

### Endpoint: `POST /api/student`

Retrieve student data by providing KTU credentials.

**Request:**
```bash
curl -X POST http://localhost:5000/api/student \
  -H "Content-Type: application/json" \
  -d '{"username":"stu123","password":"yourpassword"}'
```

**Success Response (200):**
```json
{
  "request_info": {
    "timestamp": "2025-12-09T19:56:30Z",
    "username": "stu123"
  },
  "personal": { ... },
  "admission_details": { ... },
  "contact_details": { ... },
  "curriculum": { ... }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "status": "error",
  "error_message": "Login failed. Please check credentials."
}
```

**Error Response (500 Server Error):**
```json
{
  "status": "error",
  "error_message": "Server-side scraping error."
}
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable      | Default  | Description                              |
|---------------|----------|------------------------------------------|
| `SERVER_PORT` | `5000`  | Port where Flask app listens             |
| `LOG_LEVEL`   | `INFO`   | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### Logging

Logs are written to **stdout** with color-coded levels:
- 🟢 **INFO** — Green
- 🟡 **WARNING** — Yellow
- 🔴 **ERROR** — Red (bold)

Example log output:
```
2025-12-09 19:56:30 INFO __main__ Starting Flask app host=0.0.0.0 port=5000
2025-12-09 19:56:32 INFO werkzeug * Running on http://127.0.0.1:5000
```

Change verbosity by setting `LOG_LEVEL=DEBUG` in `.env`.

---

## 📂 Project Structure

```
KTU API/
├── app.py                  # Main Flask application
├── scraper.py              # KTU data scraping logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md               # This file
├── result.json             # JSON schema/template
└── website/
    └── index.html          # Web interface (dark theme)
```

---

## 🛠️ Development

### Run in Debug Mode
```bash
# Set LOG_LEVEL=DEBUG in .env
py app.py
```

### Production Deployment (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

<div align="center">

**Built with ❤️ for KTU Students**

[⬆ Back to Top](#-ktu-api-scraper)

</div>

