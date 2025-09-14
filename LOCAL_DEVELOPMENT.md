# Running the Resume Site Locally

This guide explains how to set up and run the resume site on your own machine for development or preview.

## Prerequisites

- Python 3.10 or newer
- `pip` for installing dependencies
- (Optional) `virtualenv` or the built-in `venv` module

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resume-site
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .\.venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the development server**
   Run from the repository root so Python can locate the `app` package:
   ```bash
   uvicorn app.main:app --reload
   ```
   If you prefer to start the server from inside the `app/` directory, use:
   ```bash
   cd app
   uvicorn main:app --reload
   ```

5. **View the site in your browser**
   Visit the following URLs after the server starts:
   - Home page: <http://localhost:8000/>
   - Resume: <http://localhost:8000/resume>
   - Projects: <http://localhost:8000/projects>
   - Education: <http://localhost:8000/education>
   - About: <http://localhost:8000/about>
   - Raw resume data (JSON): <http://localhost:8000/api/resume>

6. **Run tests**
   To verify that everything is working, run the test suite:
   ```bash
   pytest
   ```

If any page returns `404` or lacks content, double-check that the server was started using the `app.main:app` module path when running from the project root. Using `uvicorn main:app --reload` outside the `app/` directory will not load the application correctly.
