# Resume LaTeX Rendering Service

A small FastAPI service that renders structured resume data into a PDF using a Jinja2 LaTeX template and the `tectonic` compiler.

This repository provides an HTTP API with two paths:

- `POST /render-resume`: structured resume JSON -> LaTeX template -> PDF
- `POST /render-latex`: raw LaTeX -> PDF
- `POST /render-latex-raw`: raw `text/plain` LaTeX body -> PDF
- `POST /render-tex-file`: uploaded `.tex` file -> PDF

The service:

- Validates resume payloads using Pydantic models in `app/models.py`
- Renders LaTeX from `app/templates/resume_template.tex.j2`
- Compiles LaTeX to PDF with `tectonic`
- Writes the last generated LaTeX to a debug file in the repo root

## Contents

- `app/main.py`: FastAPI application and endpoints
- `app/models.py`: request and resume schema models
- `app/latex_renderer.py`: LaTeX rendering and compilation logic
- `app/templates/resume_template.tex.j2`: resume LaTeX template
- `Dockerfile`: container image for the API and `tectonic`
- `docker-compose.yml`: local development startup with Docker Compose
- `requirements.txt`: Python dependencies

## Quickstart With Docker Compose

This is the easiest way to run the service on local Windows.

Prerequisites:

- Docker Desktop installed
- Docker Desktop running
- `docker compose` available in your terminal

From the repository root:

```bash
docker compose up --build
```

The API will start on:

```text
http://127.0.0.1:8000
```

To stop it:

```bash
docker compose down
```

Development behavior:

- The repo is mounted into the container with `.:/app`
- Uvicorn runs with `--reload`
- `debug_resume.tex` and `debug_raw_latex.tex` are written into the repo root on your Windows filesystem

## API

## Production Integration

Live API base URL:

```text
https://latex-resume-engine.onrender.com
```

Recommended production flow:

1. The frontend user clicks `Download PDF`.
2. Your backend loads the full LaTeX document from the database.
3. Your backend sends that LaTeX string to this renderer service.
4. This service compiles the LaTeX and returns PDF bytes.
5. Your backend streams that PDF back to the browser with a download response.

Recommended endpoint:

- `POST /render-latex-raw`

Why this endpoint:

- It accepts the full LaTeX content exactly as stored.
- It avoids JSON escaping issues with backslashes.
- It avoids temporary `.tex` file upload handling in your backend.
- It returns `application/pdf` directly.

Backend request contract:

- URL: `https://latex-resume-engine.onrender.com/render-latex-raw`
- Method: `POST`
- Header: `Content-Type: text/plain`
- Body: full LaTeX source from the database

Expected response:

- `200 OK`
- `Content-Type: application/pdf`
- Response body: PDF bytes

Example backend fetch:

```ts
const latex = resume.latexSource;

const response = await fetch("https://latex-resume-engine.onrender.com/render-latex-raw", {
  method: "POST",
  headers: {
    "Content-Type": "text/plain",
  },
  body: latex,
});

if (!response.ok) {
  throw new Error(`PDF render failed: ${response.status}`);
}

const pdfBuffer = Buffer.from(await response.arrayBuffer());
```

Recommended backend response to the browser:

- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename="resume.pdf"`

Important architecture note:

- The frontend should call your backend, not this renderer service directly.
- Your backend should remain responsible for auth, database access, error handling, and returning the final download response.

### `POST /render-resume`

Render a structured resume payload into a PDF.

Request body:

```json
{
  "resume": {
    "header": {
      "name": "Jane Developer",
      "phone": "(555) 555-5555",
      "email": "jane@example.com",
      "location": "San Francisco, CA",
      "links": {
        "portfolio": "https://example.com",
        "linkedin": "https://linkedin.com/in/jane",
        "github": "https://github.com/jane"
      }
    },
    "summary": "Short professional summary...",
    "education": [
      {
        "school": "University",
        "degree": "B.S.",
        "location": "City",
        "startDate": "2016",
        "endDate": "2020"
      }
    ],
    "experience": [
      {
        "title": "Software Engineer",
        "company": "Acme",
        "location": "Remote",
        "startDate": "2021",
        "endDate": "Present",
        "bullets": ["Did X", "Did Y"]
      }
    ],
    "projects": [
      {
        "name": "Project A",
        "stack": "Python, FastAPI",
        "year": "2024",
        "bullets": ["Built feature A"]
      }
    ],
    "skills": {
      "languages": ["Python"],
      "frameworks": ["FastAPI"],
      "databases": ["Postgres"],
      "cloud": ["AWS"],
      "concepts": ["TDD"]
    }
  }
}
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/render-resume" \
  -H "Content-Type: application/json" \
  --data-binary @examples/resume-payload.json \
  --output resume.pdf
```

### `POST /render-latex`

Compile raw LaTeX directly into a PDF.

Request body:

```json
{
  "latex": "\\documentclass{article}\n\\begin{document}\nHello from LaTeX\n\\end{document}"
}
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/render-latex" \
  -H "Content-Type: application/json" \
  --data-binary @examples/latex-payload.json \
  --output resume.pdf
```

Success response:

- `200 OK` with `application/pdf`

Error responses:

- `422` for request validation errors
- `500` for LaTeX rendering or compilation failures

If compilation fails, inspect `debug_resume.tex` or `debug_raw_latex.tex` in the repo root.

### `POST /render-latex-raw`

Send the full LaTeX document as the raw request body with `Content-Type: text/plain`.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/render-latex-raw" \
  -H "Content-Type: text/plain" \
  --data-binary @resume.tex \
  --output resume.pdf
```

This is the simplest integration when your backend already stores the full LaTeX string in a database.

### `POST /render-tex-file`

Upload a `.tex` file directly as multipart form data and receive a PDF.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/render-tex-file" \
  -F "file=@resume.tex" \
  --output resume.pdf
```

Notes:

- The uploaded file must have a `.tex` extension.
- The uploaded file must be UTF-8 encoded.
- If compilation fails, inspect `debug_uploaded.tex` in the repo root.

## Local Non-Docker Option

If you want to run it directly on the host instead:

1. Install Python 3.10+.
2. Install `tectonic` and ensure it is on `PATH`.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

## Notes

- The LaTeX escaping filter intentionally does not escape backslashes.
- `/render-latex` assumes the client sends valid full LaTeX.
- The service currently shells out to `tectonic` with `subprocess.run(...)`.
- There is no compile timeout yet.
