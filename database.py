"""
HireFlow AI - SQLite Database Layer
Stores recruitment, employee, onboarding, document, and activity records.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hireflow.db")


def get_connection():
    """Get a thread-safe connection to SQLite database."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables with the academic project schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Job Openings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Job_Openings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        department TEXT NOT NULL,
        experience_required TEXT NOT NULL,
        skills_required TEXT NOT NULL,
        salary_range TEXT NOT NULL,
        job_description TEXT,
        status TEXT DEFAULT 'Open',
        created_at TEXT NOT NULL
    )
    """)

    # 2. Candidates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        experience_years TEXT,
        education TEXT,
        skills TEXT,
        match_score INTEGER DEFAULT 0,
        matching_skills TEXT,
        missing_skills TEXT,
        ai_summary TEXT,
        ai_recommendation TEXT DEFAULT 'Pending Review',
        status TEXT DEFAULT 'Applied',
        resume_filename TEXT,
        applied_date TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES Job_Openings(id)
    )
    """)

    # 3. Employees table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT UNIQUE NOT NULL,
        candidate_id INTEGER,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        joining_date TEXT NOT NULL,
        reporting_manager TEXT NOT NULL,
        status TEXT DEFAULT 'Onboarding',
        created_at TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES Candidates(id)
    )
    """)

    # 4. Onboarding Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Onboarding_Tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        task_name TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        due_date TEXT,
        completed_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
    )
    """)

    # 5. Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT NOT NULL,
        document_name TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        notes TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
    )
    """)

    # 6. Interview Records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Interview_Records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        job_id INTEGER,
        interview_date TEXT NOT NULL,
        interviewer TEXT NOT NULL,
        round TEXT NOT NULL,
        questions_generated TEXT,
        feedback TEXT,
        status TEXT DEFAULT 'Scheduled',
        created_at TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES Candidates(id),
        FOREIGN KEY (job_id) REFERENCES Job_Openings(id)
    )
    """)

    # 7. HR Activities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS HR_Activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action_type TEXT NOT NULL,
        description TEXT NOT NULL,
        actor TEXT DEFAULT 'HR Admin'
    )
    """)

    conn.commit()
    conn.close()


def log_activity(action_type: str, description: str, actor: str = "HR Admin"):
    """Record an audit log entry for HR or AI Agent actions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO HR_Activities (timestamp, action_type, description, actor)
    VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action_type, description, actor))
    conn.commit()
    conn.close()


def get_activities(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieve recent HR activity logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM HR_Activities ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# --- Job Openings Methods ---

def create_job(title: str, department: str, experience: str, skills: str, salary: str, description: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO Job_Openings (title, department, experience_required, skills_required, salary_range, job_description, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)
    """, (title, department, experience, skills, salary, description, created_at))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_activity("JOB_CREATED", f"Created job opening: {title} ({department})", "HR Admin")
    return job_id


def get_all_jobs() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Job_Openings ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Job_Openings WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_job(job_id: int, title: str, department: str, experience: str, skills: str, salary: str, description: str, status: str = 'Open'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE Job_Openings
    SET title=?, department=?, experience_required=?, skills_required=?, salary_range=?, job_description=?, status=?
    WHERE id=?
    """, (title, department, experience, skills, salary, description, status, job_id))
    conn.commit()
    conn.close()
    log_activity("JOB_UPDATED", f"Updated job opening ID {job_id}: {title}", "HR Admin")


# --- Candidate Methods ---

def add_candidate(job_id: Optional[int], name: str, email: str, phone: str, experience_years: str,
                  education: str, skills: str, match_score: int, matching_skills: str,
                  missing_skills: str, ai_summary: str, ai_recommendation: str,
                  resume_filename: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    applied_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO Candidates (job_id, name, email, phone, experience_years, education, skills,
                            match_score, matching_skills, missing_skills, ai_summary,
                            ai_recommendation, status, resume_filename, applied_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Applied', ?, ?)
    """, (job_id, name, email, phone, experience_years, education, skills, match_score,
          matching_skills, missing_skills, ai_summary, ai_recommendation, resume_filename, applied_date))
    cand_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_activity("CANDIDATE_ADDED", f"Candidate {name} submitted for job #{job_id or 'General'}", "HireFlow AI Agent")
    return cand_id


def get_all_candidates(job_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT c.*, j.title as job_title, j.department as job_department
    FROM Candidates c
    LEFT JOIN Job_Openings j ON c.job_id = j.id
    WHERE 1=1
    """
    params = []
    if job_id:
        query += " AND c.job_id = ?"
        params.append(job_id)
    if status and status != "All":
        query += " AND c.status = ?"
        params.append(status)
    query += " ORDER BY c.id DESC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_candidate_by_id(candidate_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.*, j.title as job_title, j.department as job_department, j.skills_required as job_skills
    FROM Candidates c
    LEFT JOIN Job_Openings j ON c.job_id = j.id
    WHERE c.id = ?
    """, (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_candidate_status(candidate_id: int, new_status: str, actor: str = "HR Admin"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
    conn.commit()
    conn.close()
    log_activity("STATUS_CHANGE", f"Candidate #{candidate_id} status changed to '{new_status}'", actor)


# --- Interview Methods ---

def schedule_interview(candidate_id: int, job_id: Optional[int], interview_date: str, interviewer: str,
                       round_name: str, questions: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO Interview_Records (candidate_id, job_id, interview_date, interviewer, round, questions_generated, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, 'Scheduled', ?)
    """, (candidate_id, job_id, interview_date, interviewer, round_name, questions, created_at))
    interview_id = cursor.lastrowid
    # Automatically update candidate status to 'Interview Scheduled'
    cursor.execute("UPDATE Candidates SET status = 'Interview Scheduled' WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    log_activity("INTERVIEW_SCHEDULED", f"Interview scheduled for Candidate #{candidate_id} with {interviewer}", "HR Admin")
    return interview_id


def get_interviews_for_candidate(candidate_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT ir.*, c.name as candidate_name, j.title as job_title
    FROM Interview_Records ir
    JOIN Candidates c ON ir.candidate_id = c.id
    LEFT JOIN Job_Openings j ON ir.job_id = j.id
    WHERE ir.candidate_id = ?
    ORDER BY ir.id DESC
    """, (candidate_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_interviews() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT ir.*, c.name as candidate_name, c.email as candidate_email, j.title as job_title
    FROM Interview_Records ir
    JOIN Candidates c ON ir.candidate_id = c.id
    LEFT JOIN Job_Openings j ON ir.job_id = j.id
    ORDER BY ir.id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# --- Employee & Onboarding Methods ---

STANDARD_DOCUMENTS = [
    "Resume / CV",
    "Aadhaar / National ID / PAN",
    "Educational Degree Certificates",
    "Bank Account Details & Cancelled Cheque",
    "Passport Size Photograph",
    "Signed Offer Letter",
    "Signed Employment Agreement"
]

STANDARD_ONBOARDING_TASKS = [
    ("Employee Profile Creation", "Profile", 1),
    ("Document Verification", "Verification", 2),
    ("Corporate Email Account Setup", "IT Setup", 3),
    ("Biometric & ID Card Generation", "HR & Admin", 3),
    ("Workstation & Software Allocation", "IT Setup", 4),
    ("Department & Manager Assignment", "HR & Admin", 5),
    ("Orientation & Policy Briefing", "Orientation", 7),
]


def register_employee(candidate_id: Optional[int], name: str, email: str, department: str,
                      designation: str, joining_date: str, reporting_manager: str) -> str:
    """Register selected candidate as employee and initialize standard onboarding checklist & docs."""
    conn = get_connection()
    cursor = conn.cursor()

    # Generate employee ID (e.g. EMP-2026-001)
    cursor.execute("SELECT COUNT(*) FROM Employees")
    count = cursor.fetchone()[0] + 1
    emp_id = f"EMP-{datetime.now().year}-{count:03d}"

    created_at = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO Employees (employee_id, candidate_id, name, email, department, designation, joining_date, reporting_manager, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Onboarding', ?)
    """, (emp_id, candidate_id, name, email, department, designation, joining_date, reporting_manager, created_at))

    # If linked to candidate, mark candidate as Selected
    if candidate_id:
        cursor.execute("UPDATE Candidates SET status = 'Selected' WHERE id = ?", (candidate_id,))

    # Seed Standard Onboarding Tasks
    for task_name, category, days_due in STANDARD_ONBOARDING_TASKS:
        cursor.execute("""
        INSERT INTO Onboarding_Tasks (employee_id, task_name, category, status, due_date)
        VALUES (?, ?, ?, 'Pending', date('now', ?))
        """, (emp_id, task_name, category, f"+{days_due} days"))

    # Seed Standard Documents Checklist
    for doc in STANDARD_DOCUMENTS:
        cursor.execute("""
        INSERT INTO Documents (employee_id, document_name, status, notes, updated_at)
        VALUES (?, ?, 'Pending', 'Awaiting verification', ?)
        """, (emp_id, doc, created_at))

    conn.commit()
    conn.close()

    log_activity("EMPLOYEE_REGISTERED", f"Registered new employee {name} ({emp_id}) in {department}", "HR Admin")
    return emp_id


def get_all_employees() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employees ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_employee_by_id(emp_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employees WHERE employee_id = ?", (emp_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_onboarding_tasks(employee_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Onboarding_Tasks WHERE employee_id = ? ORDER BY id ASC", (employee_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_onboarding_task(task_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == "Completed" else None
    cursor.execute("""
    UPDATE Onboarding_Tasks SET status = ?, completed_at = ? WHERE id = ?
    """, (new_status, completed_at, task_id))
    conn.commit()
    conn.close()
    log_activity("TASK_UPDATED", f"Onboarding task #{task_id} updated to {new_status}", "HR Admin")


def get_documents_for_employee(employee_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Documents WHERE employee_id = ? ORDER BY id ASC", (employee_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_document_status(doc_id: int, new_status: str, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE Documents SET status = ?, notes = ?, updated_at = ? WHERE id = ?
    """, (new_status, notes, now_str, doc_id))
    conn.commit()
    conn.close()
    log_activity("DOC_VERIFIED", f"Document #{doc_id} status updated to {new_status}", "HR Admin")


# --- Metrics & Stats ---

def get_dashboard_metrics() -> Dict[str, Any]:
    """Calculate aggregated metrics for the HR Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Candidates")
    total_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Candidates WHERE status = 'Shortlisted'")
    shortlisted_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Candidates WHERE status = 'Interview Scheduled'")
    interviews_scheduled = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Candidates WHERE status = 'Selected'")
    selected_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Employees")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Onboarding_Tasks WHERE status != 'Completed'")
    pending_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Job_Openings WHERE status = 'Open'")
    open_jobs = cursor.fetchone()[0]

    # Status distribution
    cursor.execute("SELECT status, COUNT(*) as count FROM Candidates GROUP BY status")
    status_distribution = {row['status']: row['count'] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_candidates": total_candidates,
        "shortlisted_candidates": shortlisted_candidates,
        "interviews_scheduled": interviews_scheduled,
        "selected_candidates": selected_candidates,
        "total_employees": total_employees,
        "pending_tasks": pending_tasks,
        "open_jobs": open_jobs,
        "status_distribution": status_distribution
    }


def seed_sample_data():
    """Populate database with realistic demo data for the academic demonstration."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM Job_Openings")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # 1. Seed Jobs
    jobs = [
        (
            "Senior Python Developer",
            "Engineering",
            "4-6 years",
            "Python, Django, FastAPI, PostgreSQL, Docker, REST APIs, Git",
            "₹14,00,000 - ₹20,00,000 PA",
            "We are seeking an experienced Senior Python Developer to design and build scalable microservices, optimize high-throughput REST APIs, and mentor junior developers in clean architecture.",
            "Open",
            "2026-11-01"
        ),
        (
            "Data Analyst",
            "Data & Analytics",
            "2-4 years",
            "Python, SQL, Power BI, Pandas, Tableau, Statistics, Excel",
            "₹8,00,000 - ₹12,00,000 PA",
            "Seeking an analytical Data Analyst to transform complex datasets into actionable business intelligence dashboards, KPI reports, and automated data pipelines.",
            "Open",
            "2026-11-03"
        ),
        (
            "HR Operations Specialist",
            "Human Resources",
            "3-5 years",
            "Recruitment, Employee Onboarding, HRMS, Payroll, Conflict Resolution, Compliance",
            "₹7,00,000 - ₹10,50,000 PA",
            "Looking for an energetic HR Operations Specialist to oversee talent acquisition, streamline new hire onboarding lifecycles, and maintain HR compliance records.",
            "Open",
            "2026-11-05"
        )
    ]

    cursor.executemany("""
    INSERT INTO Job_Openings (title, department, experience_required, skills_required, salary_range, job_description, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, jobs)

    # 2. Seed Candidates
    candidates = [
        (
            1, "Priya Sharma", "priya.sharma@example.com", "+91 98765 43210", "5 years",
            "B.Tech Computer Science, NIT Trichy",
            "Python, FastAPI, Django, PostgreSQL, Docker, AWS, Redis, Git",
            92, "Python, FastAPI, Django, PostgreSQL, Docker, Git", "None (Exceeds core requirements)",
            "Strong candidate with 5 years building scalable backend services and distributed microservices with FastAPI and Docker.",
            "Strong Match", "Shortlisted", "Priya_Sharma_Python_Dev.pdf", "2026-11-04"
        ),
        (
            1, "Vikram Malhotra", "vikram.m@example.com", "+91 98112 34567", "3.5 years",
            "B.E. Information Technology, Pune University",
            "Python, Flask, MySQL, REST APIs, Git",
            75, "Python, REST APIs, Git", "Docker, FastAPI, PostgreSQL",
            "Solid foundational Python developer with REST API experience; needs mentoring on Docker and FastAPI.",
            "Potential Match", "Applied", "Vikram_Malhotra_Resume.pdf", "2026-11-06"
        ),
        (
            2, "Rahul Verma", "rahul.verma@example.com", "+91 99887 66554", "3 years",
            "B.Sc Statistics & Data Science, Delhi University",
            "Python, SQL, Power BI, Pandas, Tableau, Excel, Data Modeling",
            88, "Python, SQL, Power BI, Pandas, Tableau, Excel", "Advanced Statistics",
            "Experienced data analyst proficient in Power BI dashboards, SQL querying, and automated reporting.",
            "Strong Match", "Interview Scheduled", "Rahul_Verma_Data_Analyst.pdf", "2026-11-05"
        ),
        (
            3, "Ananya Iyer", "ananya.iyer@example.com", "+91 97654 32109", "4 years",
            "MBA in Human Resources, Symbiosis",
            "Recruitment, Employee Onboarding, HRMS, Payroll, Employee Engagement, Compliance",
            95, "Recruitment, Employee Onboarding, HRMS, Payroll, Compliance", "None",
            "Outstanding HR professional with proven track record in end-to-end recruitment lifecycle and employee retention.",
            "Strong Match", "Selected", "Ananya_Iyer_HR_Specialist.pdf", "2026-11-02"
        ),
        (
            1, "Amit Joshi", "amit.j@example.com", "+91 98223 34455", "1 year",
            "BCA, Bangalore University",
            "C++, Java, Basic Python",
            40, "Python (basic)", "FastAPI, Django, PostgreSQL, Docker, AWS",
            "Candidate lacks required 4+ years of backend microservice development experience.",
            "Low Match", "Rejected", "Amit_Joshi_Resume.pdf", "2026-11-07"
        )
    ]

    cursor.executemany("""
    INSERT INTO Candidates (job_id, name, email, phone, experience_years, education, skills,
                            match_score, matching_skills, missing_skills, ai_summary,
                            ai_recommendation, status, resume_filename, applied_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, candidates)

    # 3. Seed Interview Record for Rahul Verma
    cursor.execute("""
    INSERT INTO Interview_Records (candidate_id, job_id, interview_date, interviewer, round, questions_generated, status, created_at)
    VALUES (3, 2, '2026-11-12 11:00 AM', 'Dr. Arvind Sen (VP Analytics)', 'Technical Round 1',
    '1. How do you optimize complex SQL joins across large partitioned tables?\n2. Describe a time you built an executive KPI dashboard in Power BI.\n3. How do you handle missing or anomalous data in Pandas?',
    'Scheduled', '2026-11-06')
    """)

    # 4. Seed Employee: Ananya Iyer (Selected candidate)
    emp_id = "EMP-2026-001"
    cursor.execute("""
    INSERT INTO Employees (employee_id, candidate_id, name, email, department, designation, joining_date, reporting_manager, status, created_at)
    VALUES (?, 4, 'Ananya Iyer', 'ananya.iyer@hireflow.internal', 'Human Resources', 'HR Operations Specialist', '2026-11-15', 'Meera Kapoor (HR Director)', 'Onboarding', '2026-11-08')
    """, (emp_id,))

    # Seed initial onboarding tasks for Ananya
    for task_name, category, days in STANDARD_ONBOARDING_TASKS:
        status = "Completed" if category in ["Profile", "Verification"] else "Pending"
        comp_date = "2026-11-09" if status == "Completed" else None
        cursor.execute("""
        INSERT INTO Onboarding_Tasks (employee_id, task_name, category, status, due_date, completed_at)
        VALUES (?, ?, ?, ?, date('now', ?), ?)
        """, (emp_id, task_name, category, status, f"+{days} days", comp_date))

    # Seed documents for Ananya
    for idx, doc in enumerate(STANDARD_DOCUMENTS):
        status = "Verified" if idx < 3 else ("Submitted" if idx < 5 else "Pending")
        cursor.execute("""
        INSERT INTO Documents (employee_id, document_name, status, notes, updated_at)
        VALUES (?, ?, ?, 'Verified by HR compliance officer', '2026-11-09')
        """, (emp_id, doc, status))

    # 5. Seed Activities
    activities = [
        ("SYSTEM_INIT", "HireFlow AI recruitment database initialized", "System"),
        ("JOB_CREATED", "Job opening created: Senior Python Developer", "HR Admin"),
        ("RESUME_SCREENED", "AI screened candidate Priya Sharma (Match: 92%)", "HireFlow AI Agent"),
        ("STATUS_CHANGE", "Priya Sharma shortlisted for Technical Evaluation", "HR Admin"),
        ("INTERVIEW_SCHEDULED", "Technical Round 1 scheduled for Rahul Verma", "HR Admin"),
        ("EMPLOYEE_REGISTERED", "Ananya Iyer converted to Employee EMP-2026-001", "HR Admin"),
        ("TASK_COMPLETED", "Document Verification completed for EMP-2026-001", "HR Admin")
    ]

    for action, desc, actor in activities:
        cursor.execute("""
        INSERT INTO HR_Activities (timestamp, action_type, description, actor)
        VALUES (datetime('now', '-2 hours'), ?, ?, ?)
        """, (action, desc, actor))

    conn.commit()
    conn.close()


def reset_and_reseed_db():
    """Reset database tables and seed fresh 50+ candidates demo data."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()
    try:
        import generate_50_resumes
        generate_50_resumes.generate_all_and_seed_db()
    except Exception:
        seed_sample_data()

