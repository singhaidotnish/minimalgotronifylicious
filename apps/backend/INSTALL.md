# 🚀 Installation Guide for Algomin

This guide explains how to set up and run the **Algomin** project locally, including the CLI, FastAPI server, and WebSocket-based data stream observers.

---

## 📦 1. Prerequisites

Make sure you have the following installed:

- **Python 3.10+**
- **Git**
- **pip** (or optionally [Poetry](https://python-poetry.org/))
- A valid **AngelOne developer account** (for WebSocket access)

---

## 📁 2. Clone the Repository

```bash
git clone https://github.com/yourusername/algomin.git
cd algomin


python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# confirm installation
pip list | grep algomin
# you should see
algomin    0.1     (editable)

```