# 🧠 SATYON-AI

### One Search. One Answer. Multiple Sources.

**SATYON-AI** is a multi-source AI-powered search aggregation platform that combines results from Google, ChatGPT, DeepSeek, Wikipedia, StackOverflow, GitHub, Kaggle, ArXiv, and YouTube into a single, intelligent answer.

---

## ✨ Features

- **🔍 Multi-Source Search** — Query 7+ sources simultaneously
- **🤖 AI Summarization** — OpenAI & DeepSeek powered summaries
- **📊 Smart Classification** — Auto-detects query type (code, research, dataset, tutorial)
- **⚡ Developer Mode** — Focus on code-related sources
- **🔬 Research Mode** — Focus on academic sources
- **📱 Responsive Design** — Works on desktop, tablet, and mobile
- **🎨 Premium Dark UI** — Glassmorphism with GSAP animations
- **💾 Result Caching** — In-memory caching for fast repeat queries
- **🔧 Configurable** — API keys and source toggles via Settings

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Navigate to project
cd SATYON-AI

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Copy and configure environment variables
copy .env.example .env
# Edit .env with your API keys (optional)

# Start the server
python main.py
```

Open your browser to **http://localhost:8000**

### Without Backend (Demo Mode)

The frontend works without the backend! Open `frontend/index.html` directly in a browser for a demo with sample data.

---

## 🌐 Hosting on Render

This project is optimized for [Render](https://render.com).

### Easy Deploy
1. **Push** this code to a GitHub repository.
2. **Login** to Render and click **New +** > **Blueprint**.
3. **Connect** your repository. Render will automatically detect `render.yaml` and configure the service.

### Manual Configuration
If you prefer manual setup:
- **Service Type**: Web Service
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`

### Environment Variables
Set these in the Render Dashboard under **Environment**:
- `OPENAI_API_KEY`: Your key for summaries
- `SERPAPI_KEY`: Your key for Google results
- `DEBUG`: `false`

---

## 🔑 API Keys (Optional)

| Service | Key | Purpose |
|---------|-----|---------|
| OpenAI | `OPENAI_API_KEY` | AI-powered summaries |
| DeepSeek | `DEEPSEEK_API_KEY` | Alternative AI summaries |
| SerpAPI | `SERPAPI_KEY` | Google search results |
| GitHub | `GITHUB_TOKEN` | Higher rate limits |
| YouTube | `YOUTUBE_API_KEY` | Video search |

**Free APIs (no key needed):** Wikipedia, StackOverflow, ArXiv, GitHub (limited)

---

## 📁 Project Structure

```
SATYON-AI/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── search_engine.py        # Search aggregator
│   ├── ai_summarizer.py        # AI summarization
│   ├── query_classifier.py     # Query NLP
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Dependencies
│   ├── api_clients/            # Source API clients
│   │   ├── google_api.py
│   │   ├── wikipedia_api.py
│   │   ├── stackoverflow_api.py
│   │   ├── github_api.py
│   │   ├── kaggle_api.py
│   │   ├── arxiv_api.py
│   │   └── youtube_api.py
│   └── utils/
│       └── helpers.py
├── frontend/
│   ├── index.html              # Main page
│   ├── css/styles.css          # Styles
│   ├── js/
│   │   ├── app.js              # Entry point
│   │   ├── search.js           # Search logic
│   │   ├── ui.js               # UI rendering
│   │   └── animations.js       # GSAP animations
│   └── assets/
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/search?q=...` | Search all sources |
| `GET` | `/api/search/{source}?q=...` | Search specific source |
| `GET` | `/api/classify?q=...` | Classify a query |
| `GET` | `/api/sources` | List available sources |
| `GET` | `/api/health` | Health check |
| `GET` | `/docs` | Interactive API docs |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Focus search bar |
| `Enter` | Perform search |
| `Escape` | Go back to home |

---

## 🛣️ Roadmap

- [ ] Redis caching layer
- [ ] User accounts & search history
- [ ] Chrome Extension
- [ ] Android WebView app
- [ ] AI Answer Tree visualization
- [ ] Code generation feature
- [ ] Dataset Explorer with preview
- [ ] Pro tier with enhanced features

---

## 📄 License

MIT License — Built with ❤️ by SATYON-AI Team
