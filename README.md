# Python Evaluation Platform

A simple, focused Flask application for Python coding evaluation, modeled after `https://viswa.pythonanywhere.com/evaluate/2`, with a modern UI and an **Admin Portal** to inspect submissions and enter marks.

## Features

### 1. Candidate Portal (`/`)
- **Landing Page**: Dedicated entry point replacing the previous direct redirect.
- **Register New Assessment**: Enter candidate's full name to generate a new session ID and launch the workspace.
- **Resume Assessment**: Enter an existing Candidate ID to resume progress and access previously saved answers.
- **Curriculum Overview & Guidelines**: Highlights the 10 Python challenge domains and environment rules.

### 2. Candidate Evaluation Workspace (`/evaluate/<applicant_id>`)
- **Modern Interface**: Glassmorphism cards with dark/light mode toggle.
- **Monaco Code Editor**: Professional editor for each question with Python syntax highlighting.
- **Interactive Code Runner (`▶ Run Code`)**: Executes code on demand with simulated terminal output.
- **Expected Outputs Display**: Real-time expected outputs for self-checking.
- **Submit All Answers**: Saves code solutions to SQLite database (`evaluation.db`) and marks status as `Submitted`.
- **Quick Jump Navigation**: Jump bar to navigate to any question instantly.

### 3. Admin Portal & Grading (`/admin`)
- **Submissions Pipeline (`/admin`)**:
  - View all applicants with ID, Name, Submission Status (`In Progress`, `Submitted`, `Graded`), Attempted question counts, and Total Marks.
  - One-click link to open candidate's live evaluation view.
  - Button to register new applicants (`+ Register New Applicant`) with custom name.
- **Grading Cockpit (`/admin/grade/<applicant_id>`)**:
  - Review submitted code for every question.
  - **Live Code Execution**: Admin can run candidate's code in 1-click to test outputs against expected results.
  - Enter marks per question (0 - 10 scale) with quick click buttons (`0`, `5`, `10`).
  - Live total marks calculation.
  - Enter notes/feedback per question.
  - Executive overall feedback and final status (`Graded`, `Passed`, `Needs Review`, `Rejected`).

---

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
py app.py
```

3. URLs:
- **Candidate Portal (Home)**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Candidate Evaluation Workspace**: [http://127.0.0.1:5000/evaluate/2](http://127.0.0.1:5000/evaluate/2)
- **Admin Portal**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)
- **Grading Console**: [http://127.0.0.1:5000/admin/grade/2](http://127.0.0.1:5000/admin/grade/2)

---

## Running Automated Tests
```bash
py -m unittest tests/test_app.py
```
