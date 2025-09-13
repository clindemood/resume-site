# Resume Site

This repository powers an interactive resume and portfolio site built with FastAPI and vanilla HTML/JS.

## Running locally

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install fastapi uvicorn
   ```
2. Launch the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Visit <http://localhost:8000/> to browse the site.

## Running with Docker

1. Build the image:
   ```bash
   docker build -t resume-site .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 resume-site
   ```
3. Open <http://localhost:8000/> in your browser.

## Updating resume data

The site reads its resume information from JSON files under `app/`.

1. Edit `app/resume.json` with your latest overview, experience, projects, and skills.
2. Adjust `app/filesystem.json` if you want the CLI file-system demo to reflect the same details.
3. After editing, format the JSON for consistency:
   ```bash
   jq --sort-keys '.' app/resume.json > tmp && mv tmp app/resume.json
   jq --sort-keys '.' app/filesystem.json > tmp && mv tmp app/filesystem.json
   ```
4. Run tests to ensure the data loads:
   ```bash
   pytest
   ```
5. Commit and deploy the changes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on formatting JSON and submitting changes.

## Deployment

Deployment options and AWS hosting instructions are covered in [DEPLOYMENT.md](DEPLOYMENT.md).

