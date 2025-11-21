# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from .models import RenderRequest
from .latex_renderer import render_resume_to_pdf

app = FastAPI(title="Resume LaTeX Rendering Service")

@app.post("/render-resume")
async def render_resume(req: RenderRequest):
    try:
        pdf_bytes = render_resume_to_pdf(req.resume)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="resume.pdf"'
            },
        )
    except Exception as e:
        # In real app, log the error
        raise HTTPException(status_code=500, detail=str(e))
