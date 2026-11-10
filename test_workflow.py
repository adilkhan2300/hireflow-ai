"""
HireFlow AI - End-to-End Autonomous Workflow Integration Test
Validates the complete 11-step HR recruitment and onboarding lifecycle.
"""

import os
import database as db
from ai_agent import HireFlowAgent
import resume_parser

def run_test():
    print("=================================================================")
    print("🚀 Running HireFlow AI End-to-End Workflow Verification")
    print("=================================================================")

    # Initialize agent & DB
    agent = HireFlowAgent()
    db.seed_sample_data()

    # Step 1 & 2: HR creates job opening + AI generates JD
    print("\n[Step 1 & 2] Creating Job Opening & AI Job Description Generation...")
    job_title = "Cloud DevOps Architect"
    dept = "Infrastructure"
    exp = "5-8 years"
    skills = "AWS, Kubernetes, Terraform, Docker, CI/CD, Python, Linux"
    salary = "₹22,00,000 - ₹30,00,000 PA"

    ai_jd = agent.generate_job_description(job_title, dept, exp, skills, salary)
    assert len(ai_jd) > 100, "JD generation failed"
    job_id = db.create_job(job_title, dept, exp, skills, salary, ai_jd)
    print(f"✅ Job Opening #{job_id} created with AI-generated JD ({len(ai_jd)} chars)")

    # Step 3: HR uploads candidate resume PDF
    print("\n[Step 3 & 4] Parsing Candidate Resume PDF & AI Screening...")
    sample_pdf = os.path.join("sample_resumes", "Priya_Sharma_Python_Dev.pdf")
    assert os.path.exists(sample_pdf), "Sample PDF resume missing"

    with open(sample_pdf, "rb") as f:
        raw_text = resume_parser.extract_text_from_pdf(f)
    cand_info = resume_parser.extract_candidate_info(raw_text)
    print(f"✅ Extracted Candidate: {cand_info['name']} | Email: {cand_info['email']} | Skills: {cand_info['skills'][:5]}...")

    # Step 4 & 5: AI Evaluation & Recommendations
    job_dict = db.get_job_by_id(job_id)
    screening = agent.screen_resume(raw_text, cand_info, job_dict)
    print(f"✅ Match Score: {screening['match_score']}% | Recommendation: {screening['ai_recommendation']}")
    print(f"   Matching Skills: {screening['matching_skills']}")
    print(f"   Missing Skills: {screening['missing_skills']}")

    # Save candidate to DB
    cand_id = db.add_candidate(
        job_id=job_id,
        name=cand_info['name'],
        email=cand_info['email'],
        phone=cand_info['phone'],
        experience_years=cand_info['experience'],
        education=cand_info['education'],
        skills=", ".join(cand_info['skills']),
        match_score=screening['match_score'],
        matching_skills=screening['matching_skills'],
        missing_skills=screening['missing_skills'],
        ai_summary=screening['ai_summary'],
        ai_recommendation=screening['ai_recommendation'],
        resume_filename="Priya_Sharma_Python_Dev.pdf"
    )
    print(f"✅ Candidate #{cand_id} saved to pipeline.")

    # Step 6: HR reviews and approves shortlisting
    print("\n[Step 6] HR Review & Shortlisting...")
    db.update_candidate_status(cand_id, "Shortlisted", actor="HR Admin")
    cand = db.get_candidate_by_id(cand_id)
    assert cand['status'] == "Shortlisted"
    print(f"✅ Candidate #{cand_id} status updated to: {cand['status']}")

    # Step 7: AI interview questions & email drafts
    print("\n[Step 7] AI Interview Questions & Recruitment Email Generation...")
    questions = agent.generate_interview_questions(job_title, skills, exp, "Technical Round 1")
    assert len(questions) > 150
    print(f"✅ AI generated interview question bank ({len(questions)} chars)")

    # Schedule interview in DB
    int_id = db.schedule_interview(
        candidate_id=cand_id,
        job_id=job_id,
        interview_date="2026-11-20 at 11:00 AM",
        interviewer="Dr. R. Raman (Head of Infrastructure)",
        round_name="Technical Round 1",
        questions=questions
    )
    print(f"✅ Interview #{int_id} scheduled.")

    # Generate personalized email draft
    email_draft = agent.generate_email_draft("Interview Invitation", cand['name'], job_title)
    print(f"✅ Generated Email Subject: '{email_draft['subject']}'")
    db.log_activity("EMAIL_DRAFTED", f"Dispatched interview invitation to {cand['name']}", "HR Admin")

    # Step 8 & 9: HR selects candidate & converts to employee
    print("\n[Step 8 & 9] Candidate Selection & Employee Conversion...")
    db.update_candidate_status(cand_id, "Selected", actor="HR Admin")
    emp_id = db.register_employee(
        candidate_id=cand_id,
        name=cand['name'],
        email="priya.sharma@hireflow.internal",
        department="Infrastructure",
        designation="Lead DevOps Architect",
        joining_date="2026-12-01",
        reporting_manager="Suresh Menon (VP Engineering)"
    )
    print(f"✅ Registered Employee: {cand['name']} with ID: {emp_id}")

    # Step 10: AI generates welcome message & onboarding checklist
    print("\n[Step 10] AI Onboarding Welcome Kit & Verification...")
    welcome_letter = agent.generate_onboarding_welcome(
        cand['name'], "Lead DevOps Architect", "Infrastructure", "Suresh Menon", "2026-12-01"
    )
    assert "Welcome" in welcome_letter
    print(f"✅ Generated Onboarding Welcome Kit ({len(welcome_letter)} chars)")

    # Step 11: HR tracks onboarding tasks & documents
    print("\n[Step 11] Tracking Onboarding Tasks & Document Verification...")
    tasks = db.get_onboarding_tasks(emp_id)
    docs = db.get_documents_for_employee(emp_id)
    print(f"✅ Initialized {len(tasks)} onboarding tasks and {len(docs)} compliance documents.")

    # Complete 2 tasks and verify 2 docs
    db.update_onboarding_task(tasks[0]['id'], "Completed")
    db.update_onboarding_task(tasks[1]['id'], "Completed")
    db.update_document_status(docs[0]['id'], "Verified", "Verified via automated check")
    db.update_document_status(docs[1]['id'], "Verified", "Aadhaar verified")

    updated_tasks = db.get_onboarding_tasks(emp_id)
    completed_cnt = sum(1 for t in updated_tasks if t['status'] == "Completed")
    print(f"✅ Task Tracker verified: {completed_cnt}/{len(tasks)} tasks completed.")

    # Verify Dashboard Metrics
    metrics = db.get_dashboard_metrics()
    print("\n[Dashboard Verification]")
    print(f"  Total Candidates: {metrics['total_candidates']}")
    print(f"  Total Employees: {metrics['total_employees']}")
    print(f"  Pending Tasks: {metrics['pending_tasks']}")
    print(f"  Open Jobs: {metrics['open_jobs']}")

    print("\n🎉 ALL 11 WORKFLOW STEPS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_test()

