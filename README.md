# Resume Site

This repository powers an interactive resume and portfolio site built with FastAPI and vanilla HTML/JS.

## Running locally

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Launch the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Visit <http://localhost:8000/> to browse the site.

