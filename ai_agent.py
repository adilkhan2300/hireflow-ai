"""
HireFlow AI - Agent Intelligence Engine
Provides dual-mode AI operations:
1. Google Gemini Live API (when API key is provided)
2. High-Fidelity Autonomous Demo Engine (zero-setup fallback for academic evaluations)
"""

import os
import json
import re
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    """Retrieve Gemini API key from environment or Streamlit session."""
    return os.environ.get("GEMINI_API_KEY", "").strip()


def call_gemini_api(prompt: str, system_instruction: str = "", api_key: Optional[str] = None) -> Optional[str]:
    """Call Google Gemini API via REST endpoint."""
    key = api_key or get_api_key()
    if not key:
        return None

    # Supported model endpoints
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro"
    ]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
        except Exception:
            continue

    return None


class HireFlowAgent:
    """Core AI HR Agent powering recruitment and onboarding automation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_api_key()

    def is_api_active(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    # 1. Job Description Generator
    def generate_job_description(self, title: str, department: str, experience: str, skills: str, salary: str) -> str:
        system_prompt = (
            "You are an expert HR Talent Acquisition Specialist. "
            "Generate a professional, structured Job Description formatted in Markdown."
        )
        user_prompt = f"""
Create a compelling, professional Job Description for the following opening:
- Job Title: {title}
- Department: {department}
- Experience Required: {experience}
- Key Skills: {skills}
- Salary Range: {salary}

Include the following structured sections:
1. **About the Role**: A brief introductory overview (2-3 sentences).
2. **Key Responsibilities**: 5-6 clear, actionable bullet points.
3. **Required Qualifications & Skills**: Specific technical, educational, and soft skill requirements.
4. **Preferred / Nice-to-Have**: 2-3 desirable additions.
5. **What We Offer**: Competitive benefits, culture, learning opportunities.
"""
        if self.is_api_active():
            res = call_gemini_api(user_prompt, system_prompt, self.api_key)
            if res:
                return res

        # Academic Demo Engine Fallback
        return f"""### About the Role
We are seeking an enthusiastic and skilled **{title}** to join our dynamic **{department}** team. In this role, you will play a crucial part in executing key strategic projects, driving technical and operational excellence, and collaborating cross-functionally to achieve organizational objectives.

### Key Responsibilities
- Architect, build, and optimize high-quality solutions aligned with business and product roadmaps.
- Leverage **{skills}** to deliver robust, scalable, and maintainable systems.
- Collaborate with multidisciplinary stakeholders across engineering, product, and management.
- Participate in design reviews, quality audits, and continuous improvement initiatives.
- Mentor junior team members and champion standard operating procedures and best practices.
- Ensure all deliverables adhere to strict performance, reliability, and security guidelines.

### Required Qualifications & Skills
- **Experience**: {experience} of proven hands-on industry experience in relevant domains.
- **Core Skills**: Demonstrated expertise in **{skills}**.
- Solid problem-solving aptitude, logical reasoning, and analytical mindset.
- Excellent verbal and written communication skills with strong team orientation.
- Bachelor's or Master's degree in relevant discipline or equivalent practical experience.

### Preferred / Nice-to-Have
- Exposure to cloud technologies, modern CI/CD automation, or Agile frameworks.
- Prior experience working in high-growth, fast-paced startup or enterprise environments.

### What We Offer
- **Compensation**: {salary} with performance-linked annual incentives.
- Comprehensive health insurance and wellness benefits for employee and family.
- Flexible hybrid working arrangements and generous paid time off.
- Continuous learning stipends, certification support, and clear leadership growth paths.
"""

    # 2. Resume Screening & Match Scoring
    def screen_resume(self, resume_text: str, candidate_info: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate candidate resume against job opening.
        Returns match score (0-100), matching skills, missing skills, candidate summary, and recommendation.
        """
        job_title = job.get("title", "Position")
        job_skills_str = job.get("skills_required", "")
        job_exp_str = job.get("experience_required", "")
        cand_skills = candidate_info.get("skills", [])

        # Clean required skills list
        req_skills = [s.strip() for s in re.split(r'[,|/]', job_skills_str) if s.strip()]

        if self.is_api_active():
            system_prompt = (
                "You are an AI Recruitment Screening Agent. Evaluate candidate resumes against job requirements. "
                "Output strictly a JSON object with keys: match_score (integer 0-100), matching_skills (list of strings), "
                "missing_skills (list of strings), ai_summary (string 2-3 sentences), recommendation (one of 'Strong Match', 'Potential Match', 'Low Match')."
            )
            user_prompt = f"""
Job Title: {job_title}
Required Experience: {job_exp_str}
Required Skills: {job_skills_str}

Candidate Name: {candidate_info.get('name')}
Candidate Experience: {candidate_info.get('experience')}
Candidate Education: {candidate_info.get('education')}
Candidate Extracted Skills: {', '.join(cand_skills)}

Resume Text:
{resume_text[:2500]}

Analyze and return strictly valid JSON:
{{
  "match_score": <0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skillA"],
  "ai_summary": "Concise evaluation...",
  "recommendation": "Strong Match" | "Potential Match" | "Low Match"
}}
"""
            res = call_gemini_api(user_prompt, system_prompt, self.api_key)
            if res:
                try:
                    # Clean any markdown code blocks
                    cleaned = re.sub(r'```json\s*|\s*```', '', res).strip()
                    parsed = json.loads(cleaned)
                    return {
                        "match_score": int(parsed.get("match_score", 70)),
                        "matching_skills": ", ".join(parsed.get("matching_skills", [])),
                        "missing_skills": ", ".join(parsed.get("missing_skills", [])) or "None identified",
                        "ai_summary": parsed.get("ai_summary", "Candidate exhibits relevant background for the role."),
                        "ai_recommendation": parsed.get("recommendation", "Potential Match")
                    }
                except Exception:
                    pass

        # Academic Autonomous Demo Engine Reasoning
        matching = []
        missing = []
        resume_lower = resume_text.lower()

        for req in req_skills:
            req_clean = req.lower()
            if req_clean in resume_lower or any(req_clean in cs.lower() for cs in cand_skills):
                matching.append(req)
            else:
                missing.append(req)

        total_req = max(len(req_skills), 1)
        base_ratio = len(matching) / total_req
        # Calculate score (scale 35 to 98)
        score = int(35 + (base_ratio * 58) + (min(len(cand_skills), 6) * 1.5))
        score = min(max(score, 35), 98)

        if score >= 80:
            rec = "Strong Match"
            summary = (
                f"{candidate_info.get('name', 'The candidate')} is a strong fit for {job_title} with proven proficiency in "
                f"{', '.join(matching[:4]) or 'core role requirements'}. Exceeds the foundational criteria with relevant project delivery."
            )
        elif score >= 60:
            rec = "Potential Match"
            summary = (
                f"{candidate_info.get('name', 'The candidate')} possesses core capabilities in {', '.join(matching[:3]) or 'foundational skills'}, "
                f"but would benefit from ramp-up on {', '.join(missing[:2]) or 'specialized requirements'}."
            )
        else:
            rec = "Low Match"
            summary = (
                f"{candidate_info.get('name', 'The candidate')} shows promise, but lacks critical required expertise in "
                f"{', '.join(missing[:4]) or 'mandatory role skills'} for the {job_title} vacancy."
            )

        return {
            "match_score": score,
            "matching_skills": ", ".join(matching) if matching else "General foundational skills",
            "missing_skills": ", ".join(missing) if missing else "None (Meets all core requirements)",
            "ai_summary": summary,
            "ai_recommendation": rec
        }

    # 3. Interview Question Generator
    def generate_interview_questions(self, job_title: str, skills: str, experience: str, round_type: str = "Comprehensive") -> str:
        system_prompt = (
            "You are an expert HR Technical Recruiter and Hiring Bar Raiser. "
            "Generate targeted interview questions categorized by Technical, Behavioral (STAR), and HR cultural alignment."
        )
        user_prompt = f"""
Generate an interview question kit for:
- Role: {job_title}
- Required Skills: {skills}
- Experience Level: {experience}
- Interview Round: {round_type}

Provide structured questions in Markdown:
1. **Technical / Domain Questions** (3-4 questions, include what a good answer looks like)
2. **Behavioral & Problem Solving (STAR Method)** (2-3 situational questions)
3. **HR & Cultural Fit Questions** (2 questions evaluating team dynamics, adaptability, and retention)
"""
        if self.is_api_active():
            res = call_gemini_api(user_prompt, system_prompt, self.api_key)
            if res:
                return res

        # Academic Demo Engine
        return f"""### 🛠️ 1. Technical & Domain Assessment ({round_type})

**Question 1 (Core Architecture & Skills)**
- **Question**: "Walk us through your hands-on experience using **{skills.split(',')[0] if skills else 'core technologies'}**. How have you structured production applications to ensure resilience and high performance?"
- *Evaluation Criteria*: Look for practical trade-off evaluations, modular design, error handling, and memory/speed optimization techniques.

**Question 2 (Problem Solving & Debugging)**
- **Question**: "Describe a complex production bug, bottleneck, or performance degradation you encountered recently. What diagnostic steps and profiling tools did you employ to isolate and resolve it?"
- *Evaluation Criteria*: Logical root-cause analysis, systematic troubleshooting, observability, and long-term prevention strategies.

**Question 3 (Scalability & Best Practices)**
- **Question**: "How do you enforce code quality, automated test coverage, and API versioning across teams working in **{skills}**?"
- *Evaluation Criteria*: CI/CD hygiene, unit/integration testing standards, documentation, and peer code reviews.

---

### 💡 2. Behavioral & Situational Questions (STAR Method)

**Question 4 (Conflict & Stakeholder Alignment)**
- **Question**: "Tell us about a time you had a strong disagreement with a team member or product manager regarding technical implementation or project timelines. How did you handle the situation?"
- *Evaluation Criteria*: Emotional intelligence, data-driven negotiation, respectful pushback, and commitment to organizational delivery.

**Question 5 (Ownership & Adaptability)**
- **Question**: "Describe a scenario where requirements shifted abruptly midway through a development sprint. How did you reprioritize deliverables without compromising output quality?"
- *Evaluation Criteria*: Agile mindset, clear communication, proactive risk mitigation, and calm execution under pressure.

---

### 🤝 3. HR & Cultural Alignment

**Question 6 (Motivation & Growth)**
- **Question**: "What motivated you to apply for the **{job_title}** position with our team, and how does this role align with your 3-year professional roadmap?"
- *Evaluation Criteria*: Genuine interest in company vision, realistic career expectations, and proactive continuous learning.

**Question 7 (Collaboration & Working Style)**
- **Question**: "How do you thrive in a hybrid working environment? How do you maintain transparent communication and collaboration with remote team members?"
- *Evaluation Criteria*: Self-discipline, clear asynchronous communication, and constructive team participation.
"""

    # 4. Automated Email Generator
    def generate_email_draft(self, email_type: str, candidate_name: str, job_title: str, company_name: str = "HireFlow AI Corp", extra_notes: str = "") -> Dict[str, str]:
        """Generate human-in-the-loop email drafts ready for HR review and approval."""
        if self.is_api_active():
            prompt = f"""
Draft a personalized professional HR recruitment email.
Email Type: {email_type}
Candidate Name: {candidate_name}
Job Title: {job_title}
Company: {company_name}
Additional Details/Notes: {extra_notes}

Return strictly a JSON object with:
{{
  "subject": "Email Subject Line",
  "body": "Formatted email body text..."
}}
"""
            res = call_gemini_api(prompt, "You are a courteous, professional corporate HR communications specialist.", self.api_key)
            if res:
                try:
                    cleaned = re.sub(r'```json\s*|\s*```', '', res).strip()
                    parsed = json.loads(cleaned)
                    return {"subject": parsed.get("subject", ""), "body": parsed.get("body", "")}
                except Exception:
                    pass

        # Academic Demo Engine Templates
        if "acknowledgement" in email_type.lower():
            subject = f"Application Received: {job_title} at {company_name}"
            body = f"""Dear {candidate_name},

Thank you for applying for the {job_title} position at {company_name}!

We have successfully received your application and resume. Our Talent Acquisition team, assisted by HireFlow AI screening, is currently reviewing your profile against our open requirements.

If your background aligns with our criteria, our recruitment team will reach out directly regarding next steps within 3-5 business days.

We appreciate your interest in building your career with us!

Warm regards,
Talent Acquisition Team
{company_name}
"""
        elif "interview" in email_type.lower():
            subject = f"Interview Invitation: {job_title} at {company_name}"
            body = f"""Dear {candidate_name},

Following our review of your application, we were very impressed with your background and would love to invite you for an interview for the {job_title} role at {company_name}.

Interview Details:
- Format: Video Conference (Google Meet / Microsoft Teams)
- Duration: 45 - 60 minutes
- Proposed Date/Time: [HR to Insert Date & Time]
- Meeting Link: [HR to Insert Meeting Link]
- Round: Technical & Competency Evaluation

Please let us know if the proposed schedule works for you, or feel free to suggest an alternate time slot that fits your calendar.

We look forward to speaking with you!

Best regards,
HR Operations & Recruitment
{company_name}
"""
        elif "shortlist" in email_type.lower():
            subject = f"Update on your application for {job_title} - Shortlisted!"
            body = f"""Dear {candidate_name},

Congratulations! We are pleased to inform you that your profile has been shortlisted for the {job_title} opening at {company_name}.

Our hiring panel was particularly impressed by your relevant hands-on experience and skill set. Our HR coordinator will reach out shortly with scheduling details for your formal interview rounds.

Thank you for your patience and enthusiasm!

Warm regards,
HR Recruitment Team
{company_name}
"""
        elif "selection" in email_type.lower() or "offer" in email_type.lower():
            subject = f"Offer of Employment: Congratulations on being selected for {job_title}!"
            body = f"""Dear {candidate_name},

On behalf of {company_name}, we are thrilled to offer you the position of {job_title}!

Throughout our interview process, our leadership team was exceptionally impressed by your domain expertise, problem-solving skills, and cultural alignment with our mission.

Key Offer Highlights:
- Designation: {job_title}
- Department: [Department]
- Proposed Joining Date: [Joining Date]
- Work Model: Hybrid

Your formal offer letter and compensation breakdown will be shared shortly for your electronic signature. We are eager to welcome you to our team!

Heartiest congratulations!

Sincerely,
People & Culture Team
{company_name}
"""
        else:  # Rejection
            subject = f"Update regarding your application for {job_title} at {company_name}"
            body = f"""Dear {candidate_name},

Thank you for taking the time to apply and interview for the {job_title} position at {company_name}.

While we were impressed by your background and accomplishments, we have decided to move forward with another candidate whose specific skill set more closely matches our immediate operational needs.

We sincerely appreciate the time and effort you invested in our recruitment process. We will keep your resume in our talent pool for future openings that match your profile.

We wish you every success in your ongoing professional endeavors.

Warm regards,
Talent Acquisition Team
{company_name}
"""
        return {"subject": subject, "body": body}

    # 5. Onboarding Assistant & Welcome Package
    def generate_onboarding_welcome(self, name: str, designation: str, department: str, manager: str, joining_date: str) -> str:
        """Generate personalized Day 1 welcome package and orientation roadmap."""
        return f"""# 🌟 Welcome to the Team, {name}!

We are delighted to welcome you to **HireFlow AI Corp** as our new **{designation}** in the **{department}** department!

---

### 📋 Your Key Onboarding Information
- **Employee Name**: {name}
- **Designation**: {designation}
- **Department**: {department}
- **Reporting Manager**: {manager}
- **Official Joining Date**: {joining_date}
- **Work Schedule**: Monday – Friday | 9:30 AM to 6:30 PM (IST)
- **Work Mode**: Hybrid (3 Days Office / 2 Days Remote)

---

### 🚀 Your First Week Roadmap

#### **Day 1: Welcome & Setup**
- **09:30 AM**: Virtual / In-person welcome coffee with the HR People Team.
- **10:30 AM**: IT Asset Allocation (Laptop, credentials, corporate email setup).
- **02:00 PM**: 1-on-1 introductory session with your Reporting Manager ({manager}).
- **04:00 PM**: Submission and verification of onboarding documentation.

#### **Day 2-3: Orientation & Tooling**
- Overview of company tools (Slack, Jira, GitHub/GitLab, Google Workspace, HRMS).
- Completion of mandatory InfoSec, POSH, and Data Privacy compliance modules.
- Meet your assigned Onboarding Buddy for an informal peer walk-through.

#### **Day 4-5: Team Integration**
- Attend departmental sprint standups and architecture overviews.
- Review initial 30-day goals and learning roadmap outlined by {manager}.

---

### 💡 HR Support & Assistance
If you have any questions regarding your benefits, documents, or systems, please contact the People Operations desk at **hr-support@hireflow.internal** or ask your AI Onboarding Assistant in this portal anytime!
"""

    # 6. Onboarding Policy Q&A
    def answer_onboarding_faq(self, query: str) -> str:
        """Answers employee queries regarding policies, leaves, and workplace guidelines."""
        company_policies = """
Company Guidelines & Policy Handbook:
1. Working Hours: 9:30 AM - 6:30 PM IST, Monday through Friday. Lunch break from 1:00 PM - 2:00 PM.
2. Hybrid Policy: 3 days in-office, 2 days remote flexibility per week with prior manager intimation.
3. Leave Entitlements (Annual):
   - 18 Paid Privilege Leaves (PL) credited quarterly.
   - 12 Casual Leaves (CL) for personal exigencies.
   - 10 Sick Leaves (SL) with medical certificate required for >2 consecutive days.
   - Maternity Leave: 26 weeks fully paid | Paternity Leave: 2 weeks fully paid.
4. Probation Period: 3 months from joining date, followed by a formal performance review for confirmation.
5. Insurance & Medical: ₹5,00,000 comprehensive family group health insurance covering self, spouse, and up to 2 children.
6. Dress Code: Smart casuals Monday through Thursday; casual Fridays.
7. Grievance & POSH: Zero tolerance for harassment or discrimination. Internal Complaints Committee (ICC) reached at posh@hireflow.internal.
8. Payroll Cycle: Salary credited on the last working day of every calendar month.
"""
        if self.is_api_active():
            prompt = f"""
You are the HireFlow AI Employee Onboarding Assistant.
Using the following verified company policies:
{company_policies}

Answer the employee's query accurately, warmly, and concisely in Markdown:
Employee Query: "{query}"
"""
            res = call_gemini_api(prompt, "You are an empathetic, knowledgeable HR Onboarding specialist.", self.api_key)
            if res:
                return res

        # Academic Demo Knowledge Retrieval
        q = query.lower()
        if "leave" in q or "vacation" in q or "holiday" in q or "sick" in q:
            return """### 🌴 Company Leave Policy Overview

Employees are entitled to comprehensive annual leave allowances:
- **Paid Privilege Leaves (PL)**: 18 days per calendar year (accrued quarterly).
- **Casual Leaves (CL)**: 12 days per year for unplanned personal commitments.
- **Sick Leaves (SL)**: 10 days per year. (Medical prescription needed if absent for 3+ consecutive days).
- **Parental Leaves**: 26 weeks paid maternity leave / 2 weeks paid paternity leave.
- **Application Method**: Submit leave requests via the HRMS portal at least 48 hours in advance (except medical emergencies).
"""
        elif "hour" in q or "timing" in q or "time" in q or "remote" in q or "hybrid" in q or "office" in q:
            return """### ⏰ Working Hours & Hybrid Work Model

- **Standard Hours**: Monday to Friday, **9:30 AM – 6:30 PM (IST)**.
- **Lunch Break**: 1:00 PM – 2:00 PM.
- **Hybrid Arrangement**: Our team operates on a 3:2 model — 3 days from the designated office and 2 days remote per week.
- **Attendance**: Please check in daily via the biometric terminal or our internal HRMS portal before 10:00 AM.
"""
        elif "probation" in q or "confirmation" in q:
            return """### ⏳ Probation & Confirmation Policy

- **Duration**: Standard probation is **3 months** from your official joining date.
- **Review**: At the 75-day mark, your reporting manager will schedule a collaborative 90-day milestone review.
- **Confirmation**: Upon successful completion of deliverables and peer feedback, you will receive your formal confirmation letter.
"""
        elif "insurance" in q or "medical" in q or "health" in q or "benefits" in q:
            return """### 🏥 Health & Medical Insurance Benefits

- **Coverage**: Comprehensive Group Mediclaim Insurance policy of **₹5,00,000** sum insured.
- **Covered Dependents**: Covers Employee, Spouse, and up to 2 dependent children.
- **Network**: Cashless hospitalization across 8,000+ pan-India network hospitals.
- **E-Cards**: Your MediBuddy / TPA health insurance digital card will be issued within 10 days of joining.
"""
        elif "salary" in q or "payroll" in q or "pay" in q:
            return """### 💳 Payroll & Salary Crediting

- **Pay Cycle**: Salary is processed and credited on the **last working day** of each calendar month.
- **Payslips**: Monthly itemized salary slips are available for download in the HRMS portal under *My Finance > Payslips* by the 1st of the subsequent month.
- **Tax Declaration**: Please submit your investment declarations (80C, 80D, HRA) in the portal within 30 days of joining.
"""
        else:
            return f"""### ℹ️ HR Policy Information

Regarding your question: *" {query} "*

- **General Policy**: HireFlow AI Corp fosters an open, supportive, and compliant workplace culture.
- **Standard Working Hours**: 9:30 AM – 6:30 PM IST (Monday - Friday).
- **Support Contact**: For specific inquiries, you can reach the People Operations team directly at **hr-support@hireflow.internal** or connect with your HR Business Partner.
"""

    # 7. Conversational HR Agent
    def chat_with_agent(self, user_msg: str, chat_history: List[Dict[str, str]], db_summary: Dict[str, Any]) -> str:
        """Conversational agent capable of answering HR queries, analyzing pipeline stats, and executing actions."""
        if self.is_api_active():
            system_prompt = (
                "You are 'HireFlow AI', an autonomous intelligent HR and recruitment assistant. "
                "You help HR professionals analyze applicant pipelines, generate recruitment materials, and guide employee onboarding. "
                f"Current Database Context: {json.dumps(db_summary)}. "
                "Be proactive, structured, and helpful. Use markdown bullet points and headings."
            )
            contextual_prompt = f"""
User Request: {user_msg}

Please address the user's request. If they ask about current applicants, open roles, or onboarding tasks, use the provided database statistics.
"""
            res = call_gemini_api(contextual_prompt, system_prompt, self.api_key)
            if res:
                return res

        # Autonomous Demo Engine Intent Dispatcher
        msg_lower = user_msg.lower()

        if "shortlist" in msg_lower or "show candidate" in msg_lower or "applicant" in msg_lower:
            return f"""### 📊 Current Candidate Pipeline Summary

Based on the live recruitment database:
- **Total Applicants**: {db_summary.get('total_candidates', 0)}
- **Shortlisted Candidates**: {db_summary.get('shortlisted_candidates', 0)}
- **Interviews Scheduled**: {db_summary.get('interviews_scheduled', 0)}
- **Selected Candidates**: {db_summary.get('selected_candidates', 0)}

**Key Highlight**: Candidates with match scores above 85% (such as *Priya Sharma* for Python Dev and *Rahul Verma* for Data Analyst) are recommended for immediate interview scheduling! You can review their full profiles in the **Recruitment Management** or **Resume Screening** tabs.
"""
        elif "job description" in msg_lower or "create jd" in msg_lower or "jd for" in msg_lower:
            # Extract possible title
            title = "Specialist"
            if "for" in msg_lower:
                title = user_msg.split("for")[-1].strip().rstrip(".?!")
            return f"""### 📝 Draft Job Description: {title}

**Role Overview:**
We are looking for an experienced **{title}** to join our growing team. The ideal candidate will bring deep functional expertise, strong problem-solving skills, and a track record of driving impactful projects.

**Key Responsibilities:**
- Plan, execute, and monitor domain deliverables aligned with company priorities.
- Collaborate with cross-functional team leaders to resolve technical and operational hurdles.
- Establish best practices, automated workflows, and standardized reporting.

**Recommended Action**: Navigate to the **Recruitment Management > Job Openings** tab where you can customize skills, salary brackets, and save this opening directly into SQLite!
"""
        elif "interview question" in msg_lower or "questions for" in msg_lower:
            role = "Target Role"
            if "for" in msg_lower:
                role = user_msg.split("for")[-1].strip().rstrip(".?!")
            return f"""### 🎯 Suggested Interview Questions for {role}

1. **Technical Evaluation**: "What architectural patterns or tooling have you found most effective when building systems for {role}?"
2. **Problem Solving**: "Describe a time when project specifications were ambiguous. How did you clarify requirements and deliver results?"
3. **Behavioral (STAR)**: "Tell me about a high-stakes deadline. How did you prioritize tasks and manage stakeholder expectations?"
4. **Cultural Alignment**: "What kind of team environment enables you to do your best work?"

*Tip: Use the dedicated **Interview Assistant** tab to schedule rounds and link records to candidates!*
"""
        elif "onboarding" in msg_lower or "task" in msg_lower or "checklist" in msg_lower:
            return f"""### 🚀 Onboarding Status & Checklist

- **Active Employees in Onboarding**: {db_summary.get('total_employees', 0)}
- **Pending Onboarding Tasks**: {db_summary.get('pending_tasks', 0)}

**Standard Onboarding Lifecycle**:
1. Employee Profile Creation ✅
2. Identity & Academic Document Verification 📑
3. IT Asset & Email Account Setup 💻
4. Biometric ID Card Issuance 🪪
5. Department & Manager Introduction 🤝
6. Policy & HR Orientation 🌟

You can track document submissions and toggle completion statuses in the **Onboarding Management** tab.
"""
        else:
            return f"""### 🤖 HireFlow AI Agent at your service!

I am your autonomous HR & Recruitment copilot. Here is what I can do for you:

- 📋 **Generate Job Descriptions**: Say *"Create a job description for a Cloud Architect"*
- 📄 **Resume Screening**: Screen candidate resumes with automated skill matching & scoring
- 🎯 **Interview Questions**: Say *"Generate interview questions for Senior Python Dev"*
- ✉️ **Recruitment Communications**: Draft offer letters, interview invites, and polite rejections
- 🚀 **Onboarding Assistance**: Track onboarding checklists and answer employee policy FAQs
- 📊 **Database Insights**: Ask *"Show shortlisted candidates"* or *"What is our onboarding status?"*

How would you like me to assist you right now?
"""

