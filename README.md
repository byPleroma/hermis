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
