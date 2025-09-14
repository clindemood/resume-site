# Contributing

Thanks for your interest in improving the resume site! The project is small and light on tooling, so contributions are straightforward.

## Set up your environment

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the server locally to confirm things work:
   ```bash
   uvicorn app.main:app --reload
   ```

## Editing resume data

The site's content lives in JSON files under `app/`.

- Keep keys sorted for readability.
- After editing, format the JSON to ensure deterministic output:
  ```bash
  jq --sort-keys '.' app/resume.json > tmp && mv tmp app/resume.json
  jq --sort-keys '.' app/filesystem.json > tmp && mv tmp app/filesystem.json
  ```

## Tests

Run tests before submitting changes:
```bash
pytest
```

## Pull requests

- Use descriptive commit messages.
- Open a pull request with a summary of your changes and mention any open questions.
- Ensure the site still runs locally and tests pass.

Thanks for helping out!
