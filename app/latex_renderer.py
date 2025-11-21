# app/latex_renderer.py
import os
import subprocess
import tempfile
from jinja2 import Environment, FileSystemLoader
from .models import Resume

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def latex_escape(text: str) -> str:
    """
    Escape LaTeX special characters in user text.
    """
    if text is None:
        return ""
    text = str(text)
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\~{}',
        '^': r'\^{}',
        # NOTE: we intentionally do NOT replace backslashes.
        # They are needed for LaTeX commands like \%, \textbf, etc.
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    return text


env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=False,  # disable HTML-style autoescaping for LaTeX
)
env.filters["latex_escape"] = latex_escape


def render_resume_to_pdf(resume: Resume) -> bytes:
    """
    1. Render LaTeX from template and Resume data.
    2. Save LaTeX to debug file so we can inspect it.
    3. Compile using tectonic.
    4. Return PDF bytes.
    """
    template = env.get_template("resume_template.tex.j2")
    latex_source = template.render(
        header=resume.header,
        summary=resume.summary,
        education=resume.education,
        experience=resume.experience,
        projects=resume.projects,
        skills=resume.skills,
    )

    # Always save the latest generated LaTeX so you can inspect it
    debug_path = os.path.join(os.getcwd(), "debug_resume.tex")
    try:
        with open(debug_path, "w", encoding="utf-8") as dbg:
            dbg.write(latex_source)
    except Exception:
        # If writing debug file fails, we still want the main flow to continue.
        pass

    # Use a temp directory so we don't pollute the project
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")

        # Write LaTeX source for compilation
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)
        print(f"LaTeX source written to {tex_path}")

        # Run tectonic to compile .tex -> .pdf
        cmd = ["tectonic", tex_path, "--outdir", tmpdir]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            # If compilation fails, you already have debug_resume.tex saved
            raise RuntimeError(
                f"LaTeX compilation failed. "
                f"Debug LaTeX saved to {debug_path}. "
                f"LaTeX error: {result.stderr}"
            )

        # Read PDF bytes
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return pdf_bytes
