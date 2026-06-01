# app/models.py
from pydantic import BaseModel
from typing import List, Optional

class HeaderLinks(BaseModel):
    portfolio: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class Header(BaseModel):
    name: str
    phone: str
    email: str
    location: str
    links: HeaderLinks

class EducationItem(BaseModel):
    school: str
    degree: str
    location: str
    startDate: str
    endDate: str
    gpa: Optional[str] = None

class ExperienceItem(BaseModel):
    title: str
    company: str
    location: str
    startDate: str
    endDate: str
    bullets: List[str]

class ProjectItem(BaseModel):
    name: str
    stack: str
    year: str
    bullets: List[str]

class Skills(BaseModel):
    languages: List[str]
    frameworks: List[str]
    databases: List[str]
    cloud: List[str]
    concepts: List[str]

class Resume(BaseModel):
    header: Header
    summary: str
    education: List[EducationItem]
    experience: List[ExperienceItem]
    projects: List[ProjectItem]
    skills: Skills

class RenderRequest(BaseModel):
    resume: Resume


class LatexRenderRequest(BaseModel):
    latex: str
