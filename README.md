# Hermis

> **Desktop application for AI-assisted text processing built with PyQt6.**

Hermis provides a graphical interface for rewriting, explaining, translating, summarizing, and extracting arguments from various document formats using local models or cloud APIs.

---

## ⚡ Features

- **🤖 Local AI Engine**: Connects to an OpenAI-compatible `llama.cpp` server (`/v1/chat/completions`).
- **☁️ Google Gemini Integration**: Supports Gemini API with optional key rotation across multiple tokens.
- **📄 Document Processing**:
  - **Plain Text**: Automatic encoding detection.
  - **PDF**: Text extraction via `PyMuPDF` and generation via `fpdf2`.
  - **EPUB**: Parsing through `EbookLib` and `BeautifulSoup`.
- **👁️ Optional OCR**: Optical Character Recognition using `EasyOCR`.
- **🚀 Responsive UI**: Real-time streaming generation and progress reporting in the PyQt6 GUI.

---

## 📋 Requirements

- **Python**: `3.10` or newer.
- **Desktop Environment**: Any OS capable of running Qt 6 (Linux, macOS, Windows).
- **Local AI (Optional)**: A running `llama-server` exposing `/v1/chat/completions`.
- **Gemini (Optional)**: A Google Gemini API key.

---

## 📦 Installation

Create an isolated environment and install Hermis in editable mode from the project root.

### Linux / macOS (Bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

### Running Hermis

Once installed, launch the application using either command:

```bash
hermis
# or
python -m hermis
```

---

## 🔍 Optional OCR Support

OCR is intentionally separated from the core installation due to the heavy machine-learning dependencies of `EasyOCR`.

```bash
python -m pip install -e ".[ocr]"
```

> [!NOTE]
> Hermis natively extracts text from digital PDFs out-of-the-box without requiring the OCR package.

---

## ⚙️ Configuration

Hermis does not require hardcoding API keys inside the repository. You can configure them via environment variables or external files.

### Environment Variables

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Single Gemini API key | `"your-key"` |
| `HERMIS_KEYS_FILE` | Path to local file containing multiple API keys | `.local/keys.txt` |
| `HERMIS_LLAMACPP_URL` | Base URL for `llama.cpp` server | `"http://127.0.0.1:8080"` |
| `HERMIS_LLAMACPP_MODEL` | Model identifier for `llama.cpp` | `"your-model-id"` |
| `HERMIS_OUTPUT_DIR` | Output directory for generated documents | `~/Hermis/Output` |

### Key Rotation Setup

For automatic key rotation with Gemini, store keys line-by-line in an untracked file (e.g., `.local/keys.txt`):

```env
API_KEY_1="your-key-1"
API_KEY_2="your-key-2"
```

To use a custom path:

```bash
export HERMIS_KEYS_FILE="/path/to/keys.txt"
```

---

## 🛡️ Security

> [!WARNING]
> **Never commit API keys, access tokens, generated documents, or local state to git.**
> 
> The repository's `.gitignore` excludes these paths by default. If an API key is publicly exposed, revoke it immediately and issue a replacement before proceeding.

---

## 🛠️ Development

Install development tools:

```bash
python -m pip install -e ".[dev]"
```

Run test suite:

```bash
pytest
```

Run compile check:

```bash
python -m compileall -q hermis
```

Run linter:

```bash
ruff check hermis tests
```

---

## 📂 Project Layout

```text
hermis/
├── hermis/
│   ├── __init__.py
│   ├── __main__.py
│   ├── interface.py
│   ├── main.py
│   ├── rawtxt.py
│   ├── cosmetics.py
│   └── textutils.py
├── tests/
├── pyproject.toml
├── README.md
├── .gitignore
└── .env.example
```

> The core application modules remain modular to reduce migration risk while delivering a conventional, installable Python package structure.
