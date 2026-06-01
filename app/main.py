# app/main.py
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from .models import LatexRenderRequest, RenderRequest
from .latex_renderer import compile_latex_to_pdf, render_resume_to_pdf

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


@app.post("/render-latex")
async def render_latex(req: LatexRenderRequest):
    try:
        pdf_bytes = compile_latex_to_pdf(req.latex, debug_filename="debug_raw_latex.tex")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="resume.pdf"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render-latex-raw")
async def render_latex_raw(latex: str = Body(..., media_type="text/plain")):
    try:
        pdf_bytes = compile_latex_to_pdf(latex, debug_filename="debug_raw_latex_body.tex")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="resume.pdf"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render-tex-file")
async def render_tex_file(file: UploadFile = File(...)):
    try:
        if not file.filename or not file.filename.lower().endswith(".tex"):
            raise HTTPException(status_code=400, detail="Uploaded file must have a .tex extension.")

        latex_source = (await file.read()).decode("utf-8")
        pdf_bytes = compile_latex_to_pdf(latex_source, debug_filename="debug_uploaded.tex")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="resume.pdf"'
            },
        )
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Uploaded .tex file must be UTF-8 encoded.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
