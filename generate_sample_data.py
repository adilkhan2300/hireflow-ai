"""
Script to generate realistic sample PDF resumes for testing HireFlow AI.
Uses ReportLab to generate professional PDF resumes in the sample_resumes/ directory.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes")
os.makedirs(SAMPLE_DIR, exist_ok=True)


def create_pdf_resume(filepath, name, email, phone, title, summary, skills, experience, education):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'ResumeTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#1E3A8A"),
        leading=24
    )
    subtitle_style = ParagraphStyle(
        'ResumeSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#2563EB"),
        leading=16
    )
    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#4B5563"),
        leading=13
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=10,
        spaceAfter=4,
        leading=16
    )
    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#1F2937"),
        leading=14
    )
    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor("#374151"),
        leftIndent=15,
        bulletIndent=5,
        leading=14
    )

    story = []

    # Header
    story.append(Paragraph(name, title_style))
    story.append(Paragraph(title, subtitle_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(f"Email: {email}  |  Phone: {phone}  |  LinkedIn: linkedin.com/in/{name.lower().replace(' ', '')}", contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=10))

    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 6))

    # Core Technical Skills
    story.append(Paragraph("TECHNICAL & PROFESSIONAL SKILLS", section_heading))
    skills_text = " • ".join(skills)
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 6))

    # Experience
    story.append(Paragraph("WORK EXPERIENCE", section_heading))
    for job in experience:
        role_line = f"<b>{job['role']}</b> – <i>{job['company']}</i> ({job['duration']})"
        story.append(Paragraph(role_line, body_style))
        for bullet in job['points']:
            story.append(Paragraph(f"• {bullet}", bullet_style))
        story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION & CERTIFICATIONS", section_heading))
    for edu in education:
        edu_line = f"<b>{edu['degree']}</b> – {edu['institution']} ({edu['year']})"
        story.append(Paragraph(edu_line, body_style))

    doc.build(story)


def generate_all_samples():
    # 1. Priya Sharma - Senior Python Developer
    create_pdf_resume(
        os.path.join(SAMPLE_DIR, "Priya_Sharma_Python_Dev.pdf"),
        name="Priya Sharma",
        email="priya.sharma@example.com",
        phone="+91 98765 43210",
        title="Senior Python Developer & Backend Architect",
        summary="Results-driven Senior Python Engineer with 5+ years of experience designing robust microservices, high-performance REST APIs, and asynchronous data pipelines using FastAPI, Django, Docker, and PostgreSQL. Passionate about scalable architecture and engineering best practices.",
        skills=["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "AWS", "Redis", "REST APIs", "Git", "CI/CD", "Linux"],
        experience=[
            {
                "role": "Senior Software Engineer",
                "company": "CloudPeak Technologies",
                "duration": "2023 - Present",
                "points": [
                    "Architected high-throughput REST APIs handling 4M+ daily requests using FastAPI and PostgreSQL.",
                    "Containerized 8 core services with Docker and deployed them to AWS ECS with zero-downtime CI/CD pipelines.",
                    "Decreased database query latency by 45% using Redis caching and PostgreSQL index optimization."
                ]
            },
            {
                "role": "Python Developer",
                "company": "Infosys Ltd",
                "duration": "2021 - 2023",
                "points": [
                    "Developed backend business logic in Django and managed relational data schemas.",
                    "Implemented unit and integration test suites achieving 92% code coverage with PyTest.",
                    "Mentored 3 junior software engineers on clean code and Git version control workflows."
                ]
            }
        ],
        education=[
            {"degree": "B.Tech in Computer Science & Engineering", "institution": "NIT Trichy", "year": "2021"}
        ]
    )

    # 2. Rahul Verma - Data Analyst
    create_pdf_resume(
        os.path.join(SAMPLE_DIR, "Rahul_Verma_Data_Analyst.pdf"),
        name="Rahul Verma",
        email="rahul.verma@example.com",
        phone="+91 99887 66554",
        title="Data Analyst & BI Specialist",
        summary="Analytical Data Specialist with 3+ years of experience transforming complex business datasets into intuitive dashboards, automated KPI trackers, and actionable predictive insights using SQL, Power BI, Python, and Tableau.",
        skills=["Python", "SQL", "Power BI", "Pandas", "Tableau", "Excel", "Data Modeling", "ETL", "Statistics"],
        experience=[
            {
                "role": "Data Analyst",
                "company": "Fintech Global Solutions",
                "duration": "2023 - Present",
                "points": [
                    "Created 15+ automated executive Power BI dashboards monitoring revenue, churn, and acquisition metrics.",
                    "Optimized SQL ETL pipelines processing 10GB daily transactional data, reducing processing time by 30%.",
                    "Performed exploratory statistical analysis using Python (Pandas/NumPy) to identify customer churn drivers."
                ]
            },
            {
                "role": "Junior Business Analyst",
                "company": "Mu Sigma",
                "duration": "2022 - 2023",
                "points": [
                    "Designed automated Excel models with advanced macros for weekly sales forecasting.",
                    "Collaborated with cross-functional stakeholders to document data requirements and KPIs."
                ]
            }
        ],
        education=[
            {"degree": "B.Sc in Statistics & Data Science", "institution": "Delhi University", "year": "2022"}
        ]
    )

    # 3. Ananya Iyer - HR Operations Specialist
    create_pdf_resume(
        os.path.join(SAMPLE_DIR, "Ananya_Iyer_HR_Specialist.pdf"),
        name="Ananya Iyer",
        email="ananya.iyer@example.com",
        phone="+91 97654 32109",
        title="HR Operations & Talent Acquisition Specialist",
        summary="Dedicated Human Resources professional with 4 years of expertise managing end-to-end recruitment lifecycles, employee onboarding automation, HRMS systems, compliance, and employee engagement programs.",
        skills=["Recruitment", "Talent Acquisition", "Employee Onboarding", "HRMS", "Payroll", "Compliance", "Employee Engagement", "Conflict Resolution"],
        experience=[
            {
                "role": "HR Generalist",
                "company": "Aura Systems Corp",
                "duration": "2023 - Present",
                "points": [
                    "Spearheaded recruitment for 50+ technical and operational hires with a 94% retention rate.",
                    "Digitized the company employee onboarding process, cutting new hire cycle time from 10 days to 3 days.",
                    "Administered monthly payroll, statutory compliance (PF/ESI), and HRMS employee databases."
                ]
            },
            {
                "role": "Talent Acquisition Associate",
                "company": "Tata Consultancy Services",
                "duration": "2022 - 2023",
                "points": [
                    "Sourced and screened candidates across IT engineering domains using LinkedIn Recruiter and job portals.",
                    "Coordinated campus hiring drives and conducted initial behavioral screening rounds."
                ]
            }
        ],
        education=[
            {"degree": "MBA in Human Resource Management", "institution": "Symbiosis Institute of Business", "year": "2022"},
            {"degree": "B.Com", "institution": "Mumbai University", "year": "2020"}
        ]
    )

    # 4. Kavita Patel - Full Stack Developer
    create_pdf_resume(
        os.path.join(SAMPLE_DIR, "Kavita_Patel_FullStack.pdf"),
        name="Kavita Patel",
        email="kavita.patel@example.com",
        phone="+91 98450 11223",
        title="Full Stack Software Engineer",
        summary="Full Stack Developer with 4 years of experience building modern responsive web applications with React, Node.js, TypeScript, PostgreSQL, and Docker. Strong focus on UI/UX excellence and clean modular backend design.",
        skills=["React", "Node.js", "TypeScript", "JavaScript", "PostgreSQL", "Docker", "REST APIs", "HTML", "CSS", "Tailwind", "Git"],
        experience=[
            {
                "role": "Full Stack Engineer",
                "company": "NextGen Web Apps",
                "duration": "2023 - Present",
                "points": [
                    "Built reusable React components with TypeScript and Tailwind CSS for a SaaS enterprise dashboard.",
                    "Engineered RESTful Node.js / Express microservices backed by PostgreSQL.",
                    "Implemented JWT authentication and role-based access control (RBAC)."
                ]
            }
        ],
        education=[
            {"degree": "B.E. in Information Technology", "institution": "Gujarat Technological University", "year": "2022"}
        ]
    )

    print(f"Generated 4 sample PDF resumes in {SAMPLE_DIR}")


if __name__ == "__main__":
    generate_all_samples()

