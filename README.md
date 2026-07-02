# CareerOS - AI Job Search Agent

CareerOS is an intelligent, autonomous job application assistant that streamlines the entire job search process. By leveraging AI (Gemini), browser automation (Playwright), and an agentic workflow (LangGraph), CareerOS mimics a dedicated personal recruiter. 

Instead of manually searching, filtering, tweaking resumes, and filling forms, CareerOS does the repetitive heavy lifting so you can focus on interviews.

## Features

- **Automated Job Discovery**: Scrapes job listings from multiple platforms (Indeed, LinkedIn) based on your target roles (AI Engineer, Full Stack Software Developer, Java Developer, Backend Engineer, Data Analytics, SDE1).
- **Intelligent Matching**: Evaluates job descriptions against your profile to generate a match score and decides if it's worth applying for.
- **Dynamic Resume Optimization**: Generates ATS-friendly PDF resumes tailored to include keywords from the specific job description.
- **Autonomous Application**: Utilizes Playwright to navigate job boards, fill out forms, upload resumes, and submit applications.
- **Application Tracking & Analytics**: Tracks application statuses and provides comprehensive analytics via a Next.js dashboard.

## Tech Stack

### Frontend
- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **Features**: Dashboard, Job List, Tracker, Analytics

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (local) / PostgreSQL (production) via SQLModel
- **AI/LLM**: Gemini API
- **Agent Workflow**: LangGraph
- **Browser Automation**: Playwright

## Getting Started

*(Instructions will be added once the initial setup is complete)*

## Architecture overview

1. **Job Search Agent**: Scrapes and collects job postings into the database.
2. **Matching Agent**: Reads JDs and your profile, producing a match score and a recommendation to apply or skip.
3. **Resume Optimizer**: Reads the JD and generates a tailored ATS-optimized PDF resume.
4. **Application Agent**: Uses Playwright to navigate the application form, filling in text boxes, dropdowns, and uploading the optimized resume.
5. **Tracker & Analytics**: Keeps a local record of all applied jobs, generating daily and weekly insights.

## Disclaimer

**Browser Automation Ethics**: This project uses automated form submission (Playwright). Please be aware that this may violate the Terms of Service of some job platforms. Use responsibly.
