# Resume Site

This repository powers an interactive resume and portfolio site.

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

