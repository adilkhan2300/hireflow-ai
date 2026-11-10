"""
HireFlow AI - Resume Extraction & Parsing Module
Extracts candidate information (Name, Contact, Education, Experience, Skills) from PDF resumes.
"""

import re
import io
from typing import Dict, Any, List

# Try importing pdfplumber, fallback to PyPDF2
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


COMMON_SKILLS_TAXONOMY = [
    # Programming & Frameworks
    "Python", "FastAPI", "Django", "Flask", "Java", "Spring Boot", "C++", "C#", ".NET",
    "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "Node.js", "Express",
    "HTML", "CSS", "Tailwind", "Bootstrap",
    # Data & AI
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Pandas", "NumPy", "Scikit-Learn",
    "TensorFlow", "PyTorch", "Power BI", "Tableau", "Excel", "Data Modeling", "ETL", "Statistics",
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Git", "GitHub", "Linux",
    "Terraform", "REST APIs", "Microservices",
    # HR & Management
    "Recruitment", "Talent Acquisition", "Employee Onboarding", "HRMS", "Payroll",
    "Compliance", "Employee Engagement", "Performance Management", "Conflict Resolution",
    "Agile", "Scrum", "Jira", "Project Management"
]


def extract_text_from_pdf(pdf_file) -> str:
    """Extract raw text from PDF file object (bytes or path)."""
    text = ""
    # 1. Try pdfplumber first
    if HAS_PDFPLUMBER:
        try:
            if isinstance(pdf_file, (bytes, bytearray)):
                pdf_stream = io.BytesIO(pdf_file)
            else:
                pdf_stream = pdf_file

            with pdfplumber.open(pdf_stream) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text.strip()
        except Exception:
            pass

    # 2. Try PyPDF2 fallback
    if HAS_PYPDF2:
        try:
            if isinstance(pdf_file, (bytes, bytearray)):
                pdf_stream = io.BytesIO(pdf_file)
            elif hasattr(pdf_file, "seek"):
                pdf_file.seek(0)
                pdf_stream = pdf_file
            else:
                pdf_stream = open(pdf_file, "rb")

            reader = PyPDF2.PdfReader(pdf_stream)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text.strip()
        except Exception:
            pass

    return text.strip()


def extract_candidate_info(raw_text: str) -> Dict[str, Any]:
    """Parse candidate details, skills, education, and experience from resume text."""
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    # 1. Name extraction heuristic: First non-empty prominent line
    name = "Candidate"
    for line in lines[:5]:
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and not any(w.lower() in ["resume", "curriculum", "vitae", "profile", "contact", "phone", "email"] for w in words):
            name = cleaned
            break

    # 2. Email extraction
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
    email = email_match.group(0) if email_match else "Not specified"

    # 3. Phone extraction
    phone_match = re.search(r'(?:Phone|Mobile|Contact|Tel)?[:\s]*(\+?\d[\d\s\-\(\)]{8,16}\d)', raw_text, re.IGNORECASE)
    phone = phone_match.group(1).strip() if phone_match else "Not specified"

    # 4. Experience extraction
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s*of\s*experience)?', raw_text, re.IGNORECASE)
    if exp_matches:
        experience = f"{exp_matches[0]} years"
    else:
        # Check year spans e.g. 2020 - 2024
        year_spans = re.findall(r'\b(20\d{2})\s*[-–—to]\s*(20\d{2}|present)\b', raw_text, re.IGNORECASE)
        if year_spans:
            experience = f"~{len(year_spans) * 2} years (estimated)"
        else:
            experience = "2-3 years (estimated)"

    # 5. Education extraction
    degree_keywords = [
        "B.Tech", "B.E.", "M.Tech", "M.E.", "B.Sc", "M.Sc", "BCA", "MCA",
        "MBA", "BBA", "B.Com", "M.Com", "Bachelor", "Master", "Ph.D", "Diploma"
    ]
    found_degrees = []
    for line in lines:
        for deg in degree_keywords:
            if re.search(rf'\b{re.escape(deg)}\b', line, re.IGNORECASE):
                found_degrees.append(line)
                break
    education = "; ".join(found_degrees[:2]) if found_degrees else "Graduate / Degree Holder"

    # 6. Skills extraction against comprehensive dictionary
    extracted_skills = []
    text_lower = raw_text.lower()
    for skill in COMMON_SKILLS_TAXONOMY:
        # Match as word boundary
        pattern = rf'\b{re.escape(skill.lower())}\b'
        if re.search(pattern, text_lower):
            extracted_skills.append(skill)

    # If no standard skills matched, extract anything in a "Skills" section
    if not extracted_skills:
        for idx, line in enumerate(lines):
            if "skills" in line.lower() and idx + 1 < len(lines):
                next_few = lines[idx+1:idx+3]
                for item in next_few:
                    for part in re.split(r'[,|•·/]', item):
                        if part.strip() and len(part.strip()) < 30:
                            extracted_skills.append(part.strip())

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "experience": experience,
        "education": education,
        "skills": list(dict.fromkeys(extracted_skills)),  # deduplicate preserving order
        "raw_text": raw_text
    }
