# Resume LaTeX Rendering Service

A small FastAPI service that renders structured resume data (JSON) into a PDF using a Jinja2 LaTeX template and the `tectonic` compiler.

This repository provides a lightweight HTTP API to convert a `Resume` JSON payload into a downloadable PDF (`resume.pdf`). The service:

- Validates input using Pydantic models defined in `app/models.py`.
- Renders a LaTeX source via Jinja2 template `app/templates/resume_template.tex.j2`.
- Compiles LaTeX to PDF with `tectonic` inside a temporary directory and returns the PDF bytes.
- Writes the last generated LaTeX to `debug_resume.tex` at the repository root for troubleshooting.

## Contents

- `app/`
  - `main.py` — FastAPI application exposing `/render-resume`.
  - `models.py` — Pydantic models describing the resume schema.
  - `latex_renderer.py` — Template rendering and PDF compilation logic.
  - `templates/resume_template.tex.j2` — Jinja2 LaTeX template.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — (optional) project containerization.
- `debug_resume.tex` — generated LaTeX debug file (created at runtime).

## Quickstart (macOS / Linux)

Prerequisites

- Python 3.8+ (3.10 recommended)
- `pip` or a virtual environment tool (venv/poetry)
- `tectonic` installed and available on PATH. On macOS you can install it with Homebrew:

```bash
brew install tectonic
```

1. Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Run the app with Uvicorn

```bash
uvicorn app.main:app --reload
```

The service will be available at `http://127.0.0.1:8000`.

## API

POST /render-resume

- Description: Render a resume JSON into a compiled PDF.
- Content-Type: `application/json`
- Request body: `RenderRequest` (see `app/models.py`) — a short summary of the model below.
- Success response: `200 OK` with body `application/pdf` and header `Content-Disposition: attachment; filename="resume.pdf"`.
- Error responses:
  - `422` — JSON validation error (Pydantic / FastAPI)
  - `500` — Rendering or compilation error. The LaTeX source is written to `debug_resume.tex` for inspection.

Example request shape (fields shown for clarity — see `app/models.py` for full schema):

```json
{
  "resume": {
    "header": {
      "name": "Jane Developer",
      "phone": "(555) 555-5555",
      "email": "jane@example.com",
      "location": "San Francisco, CA",
      "links": { "portfolio": "https://ex.com", "linkedin": "https://linkedin.com/in/jane" }
    },
    "summary": "Short professional summary...",
    "education": [ { "school": "University", "degree": "B.S.", "location": "City", "startDate": "2016", "endDate": "2020" } ],
    "experience": [ { "title": "Software Engineer", "company": "Acme", "location": "Remote", "startDate": "2021", "endDate": "Present", "bullets": ["Did X","Did Y"] } ],
    "projects": [ { "name": "Project A", "stack": "Python, FastAPI", "year": "2024", "bullets": ["Built feature A"] } ],
    "skills": { "languages": ["Python"], "frameworks": ["FastAPI"], "databases": ["Postgres"], "cloud": ["AWS"], "concepts": ["TDD"] }
  }
}
```

You can test quickly with curl (replace `payload.json` with your file):

```bash
curl -X POST "http://127.0.0.1:8000/render-resume" \
  -H "Content-Type: application/json" \
  --data-binary @payload.json \
  --output resume.pdf
```

If the LaTeX compilation fails, inspect `debug_resume.tex` for the generated source and check `tectonic` output in the server logs.

## Development notes

- The LaTeX escaping filter `latex_escape` intentionally does not remove backslashes so that deliberate LaTeX commands in templates or user-provided content (if intended) can remain. Be cautious when allowing arbitrary input.
- `render_resume_to_pdf` writes the last generated LaTeX to `debug_resume.tex` in the repo root to help debugging compilation errors.
- The code calls `tectonic` via `subprocess.run`. Consider adding `timeout=` and logging to avoid long-running or silent failures.

## Troubleshooting

- Error: "tectonic: command not found"
  - Install tectonic and ensure it's on PATH (see prerequisites).

- LaTeX compilation errors
  - Check `debug_resume.tex` for the generated LaTeX source.
  - Run `tectonic debug_resume.tex --outdir output_dir` to get detailed errors.

- FastAPI returns 422
  - The request JSON didn't validate against the Pydantic models. Check required fields and types.

## Suggested next steps / enhancements

- Add structured logging (e.g., `structlog` or Python `logging`) to capture compile stdout/stderr and request metadata.
- Add a `timeout` to `subprocess.run` and return a 504 when compilation times out.
- Add unit tests that call `render_resume_to_pdf` with a minimal `Resume` and assert the returned bytes start with `%PDF`.
- Provide a Docker image that includes `tectonic` so the runtime is consistent across environments.

