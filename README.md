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

## Running with Docker

1. Build the image:
   ```bash
   docker build -t resume-site .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 resume-site
   ```
   The server listens on the port specified by the `PORT` environment variable, which
   defaults to `8000`. To use a different port, set `PORT` and publish the same port:
   ```bash
   docker run -e PORT=8080 -p 8080:8080 resume-site
   ```
3. Open <http://localhost:8000/> in your browser (replace `8000` with the value of `PORT` if changed).

### Session storage

Sessions are stored in memory and automatically pruned after ``SESSION_TTL`` seconds
(default: 3600).  For horizontal scalability you can provide a Redis instance by
setting ``SESSION_REDIS_URL``.

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

