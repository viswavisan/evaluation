import os
import sys
import sqlite3
import subprocess
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
DB_PATH = '/home/opc/evaluation.db'

QUESTIONS = [
    {
        "id": 1,
        "title": "1. Basic : write code to split odd and even in the range of 1 to 10.",
        "prefill": "",
        "expected_output": "([2, 4, 6, 8, 10], [1, 3, 5, 7, 9])"
    },
    {
        "id": 2,
        "title": "2. Basic : group_anagrams(words=['eat','tea','tan','ate','nat','bat'])",
        "prefill": "",
        "expected_output": "[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]"
    },
    {
        "id": 3,
        "title": "3. Basic : flatten_dict({'a':1, 'b':{'b1':2}, 'c':[1,2,3], 'd':{'d1':{'d2':3}} })",
        "prefill": "",
        "expected_output": "{'a': 1, 'b.b1': 2, 'c': [1, 2, 3], 'd.d1.d2': 3}"
    },
    {
        "id": 4,
        "title": "4. Basic : verify_brackets ( '{[()]}' , '{[(])}' )",
        "prefill": "",
        "expected_output": "True, False"
    },
    {
        "id": 5,
        "title": "5. OOPS : debug following class",
        "prefill": """class order:
    def __init__(self, product,count):
        self.total_orders += count
    def get_order_count(self):
        return {product:count}
    def get_dict(self):
        return laptop.__dict__
        
laptop = Order("Laptop",2)
phone = Order("Phone")

print(Order.total_orders)
print(laptop.get_order_count())
print(phone.get_order_count())
print(laptop.get_dict())""",
        "expected_output": """{'total': 3}
{'Laptop': 2}
{'Phone': 1}
{'product': 'Laptop'}"""
    },
    {
        "id": 6,
        "title": "6. SQL Raw query: Get the names of employees who earn more than the average salary.",
        "prefill": """import sqlite3

def run_query(query):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary REAL)''')
    cursor.executemany('INSERT INTO employees VALUES (?, ?, ?)', [(1, 'Alice', 70000),(2, 'Bob', 50000),(3, 'Charlie', 60000),(4, 'David', 80000),(5, 'Eve', 55000)])
    cursor.execute(query)
    results = [i[0] for i in cursor.fetchall()]
    conn.close()
    return results

print(run_query('''------------------------------'''))""",
        "expected_output": "['Alice', 'David']"
    },
    {
        "id": 7,
        "title": "7. ORM : Get the names of students who got 5th highest marks by SQLAlchemy ORM",
        "prefill": """from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

#table setup
class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    marks = Column(Integer)

#db setup
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

# Sample data
students_data = [
    Student(name='Alice', marks=100),
    Student(name='Bob', marks=100),
    Student(name='Charlie', marks=99),
    Student(name='David', marks=99),
    Student(name='Eve', marks=98),
    Student(name='Frank', marks=96),
    Student(name='Grace', marks=95),
    Student(name='Tony', marks=95),
    Student(name='steve', marks=90),
]
session.add_all(students_data)
session.commit()

#answer
------------------------------------------""",
        "expected_output": "['Grace','Tony']"
    },
    {
        "id": 8,
        "title": "8. flask: Create a route /add that accepts a POST request with JSON data containing two numbers a and b, and returns their sum in JSON.",
        "prefill": """from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add')
def greet():
    _____________________
    ____________________
    if a is None or b is None:
        return jsonify({"error": "Missing numbers"}), 400
    return jsonify({"sum": a + b})

if __name__ == "__main__":
    _______________________""",
        "expected_output": ""
    },
    {
        "id": 9,
        "title": "9. Test : Write a Pytest test for a function that adds two numbers.",
        "prefill": "",
        "expected_output": ""
    },
    {
        "id": 10,
        "title": "10. pandas : merge dataframe",
        "prefill": """import ________

df1 = ({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"]
})

df2 = pd.DataFrame({
    "id": [1, 2, 4],
    "salary": [50000, 60000, 70000]
})

# Outer join keeps all rows from both DataFrames
merged = ____________________
print(merged)""",
        "expected_output": """   id     name   salary
0   1    Alice  50000.0
1   2      Bob  60000.0
2   3  Charlie      NaN
3   4      NaN  70000.0"""
    }
]

def init_db():
    if os.path.dirname(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT DEFAULT 'xxxx',
            status TEXT DEFAULT 'In Progress',
            total_marks REAL DEFAULT 0.0,
            overall_feedback TEXT,
            submitted_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            applicant_id INTEGER,
            question_id INTEGER,
            code TEXT,
            marks REAL,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (applicant_id, question_id)
        )
    ''')
    
    # Safe migrations for existing databases
    for migration in [
        "ALTER TABLE applicants ADD COLUMN status TEXT DEFAULT 'In Progress'",
        "ALTER TABLE applicants ADD COLUMN total_marks REAL DEFAULT 0.0",
        "ALTER TABLE applicants ADD COLUMN overall_feedback TEXT",
        "ALTER TABLE applicants ADD COLUMN submitted_at TIMESTAMP",
        "ALTER TABLE answers ADD COLUMN marks REAL",
        "ALTER TABLE answers ADD COLUMN notes TEXT"
    ]:
        try:
            cursor.execute(migration)
        except sqlite3.OperationalError:
            pass

    # Swap existing answers for Q2 and Q3 once if needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schema_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute("SELECT value FROM schema_meta WHERE key = 'reorder_q2_q3'")
    if not cursor.fetchone():
        cursor.execute("UPDATE answers SET question_id = -2 WHERE question_id = 2")
        cursor.execute("UPDATE answers SET question_id = 2 WHERE question_id = 3")
        cursor.execute("UPDATE answers SET question_id = 3 WHERE question_id = -2")
        cursor.execute("INSERT INTO schema_meta (key, value) VALUES ('reorder_q2_q3', 'done')")

    # Create default applicant 2 if empty
    cursor.execute('SELECT COUNT(*) FROM applicants')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO applicants (id, name, status) VALUES (2, 'xxxx', 'In Progress')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    applicant_count = cursor.execute('SELECT COUNT(*) FROM applicants').fetchone()[0]
    conn.close()
    return render_template('index.html', total_questions=len(QUESTIONS), applicant_count=applicant_count)

@app.route('/evaluate/<int:applicant_id>')
def evaluate(applicant_id):
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    applicant = cursor.execute('SELECT * FROM applicants WHERE id = ?', (applicant_id,)).fetchone()
    if not applicant:
        cursor.execute("INSERT INTO applicants (id, name, status) VALUES (?, 'xxxx', 'In Progress')", (applicant_id,))
        conn.commit()
        applicant = {'id': applicant_id, 'name': 'xxxx', 'status': 'In Progress'}

    # Get saved answers for this applicant
    rows = cursor.execute('SELECT question_id, code FROM answers WHERE applicant_id = ?', (applicant_id,)).fetchall()
    saved_answers = {r['question_id']: r['code'] for r in rows}
    conn.close()

    # Prepare questions with prefill or saved answer
    prepared_questions = []
    for q in QUESTIONS:
        item = dict(q)
        item['current_code'] = saved_answers.get(q['id'], q['prefill'])
        prepared_questions.append(item)

    return render_template('evaluate.html', applicant=applicant, questions=prepared_questions)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.get_data(as_text=True) or ''
    if not code.strip():
        return 'No code to run.'

    py_exe = sys.executable or 'py'
    try:
        res = subprocess.run(
            [py_exe, '-c', code],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = res.stdout
        if res.stderr:
            output += ('\n' if output else '') + res.stderr
        return output if output else '[Program finished with no output]'
    except subprocess.TimeoutExpired:
        return 'Timeout Error: Program took more than 5 seconds.'
    except Exception as e:
        return f'Execution error: {str(e)}'

@app.route('/submit_evaluation', methods=['POST'])
def submit_evaluation():
    data = request.get_json() or {}
    applicant_id = data.get('applicant_id')
    answers = data.get('answers', {})

    if not applicant_id:
        return 'Missing applicant id', 400

    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cursor = conn.cursor()

    # Block submission if already graded
    row = cursor.execute('SELECT status FROM applicants WHERE id = ?', (applicant_id,)).fetchone()
    if row and row[0] == 'Graded':
        conn.close()
        return 'Submission locked — this evaluation has already been graded.', 403
    
    # Save answers
    for q_id_str, code in answers.items():
        try:
            q_id = int(q_id_str)
            cursor.execute('''
                INSERT INTO answers (applicant_id, question_id, code, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(applicant_id, question_id) DO UPDATE SET
                    code = excluded.code,
                    updated_at = CURRENT_TIMESTAMP
            ''', (applicant_id, q_id, code))
        except ValueError:
            continue

    # Update applicant status to Submitted
    cursor.execute('''
        UPDATE applicants
        SET status = CASE WHEN status = 'Graded' THEN 'Graded' ELSE 'Submitted' END,
            submitted_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (applicant_id,))

    conn.commit()
    conn.close()
    return 'Answers submitted successfully!'

@app.route('/register', methods=['POST'])
def register():
    name = ''
    if request.is_json:
        data = request.get_json(silent=True) or {}
        name = data.get('name', '').strip()
    elif request.form:
        name = request.form.get('name', '').strip()

    if not name:
        name = 'Candidate'

    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO applicants (name, status) VALUES (?, 'In Progress')", (name,))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    eval_url = url_for('evaluate', applicant_id=new_id)

    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'status': 'success',
            'applicant_id': new_id,
            'name': name,
            'redirect_url': eval_url,
            'message': f'New applicant registered with ID: {new_id}. You can visit {eval_url}'
        })

    return f'New applicant registered with ID: {new_id}. You can visit {eval_url}'

@app.route('/api/applicant/<int:applicant_id>')
def get_applicant_api(applicant_id):
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    applicant = cursor.execute('SELECT id, name, status, submitted_at, total_marks FROM applicants WHERE id = ?', (applicant_id,)).fetchone()
    conn.close()

    if not applicant:
        return jsonify({'status': 'error', 'message': f'Applicant #{applicant_id} not found.'}), 404

    return jsonify({
        'status': 'success',
        'applicant': dict(applicant),
        'redirect_url': url_for('evaluate', applicant_id=applicant_id)
    })

# --- Admin Routes (Check Submissions & Enter Marks) ---

@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch applicants with answer counts and scores
    rows = cursor.execute('''
        SELECT a.*, 
               COUNT(ans.question_id) as answered_count,
               TOTAL(ans.marks) as current_marks
        FROM applicants a
        LEFT JOIN answers ans ON a.id = ans.applicant_id AND ans.code IS NOT NULL AND TRIM(ans.code) != ''
        GROUP BY a.id
        ORDER BY a.id DESC
    ''').fetchall()

    applicants_list = [dict(r) for r in rows]
    total_questions = len(QUESTIONS)
    conn.close()

    return render_template('admin.html', applicants=applicants_list, total_questions=total_questions)

@app.route('/admin/grade/<int:applicant_id>')
def admin_grade(applicant_id):
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    applicant = cursor.execute('SELECT * FROM applicants WHERE id = ?', (applicant_id,)).fetchone()
    if not applicant:
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # Fetch all answers for this applicant
    answer_rows = cursor.execute('SELECT * FROM answers WHERE applicant_id = ?', (applicant_id,)).fetchall()
    answers_by_qid = {r['question_id']: dict(r) for r in answer_rows}
    conn.close()

    # Prepare questions with candidate's submitted code and existing marks
    grading_questions = []
    total_assigned_marks = 0
    for q in QUESTIONS:
        ans = answers_by_qid.get(q['id'], {})
        submitted_code = ans.get('code', '')
        marks = ans.get('marks')
        notes = ans.get('notes', '')
        if marks is not None:
            total_assigned_marks += marks

        grading_questions.append({
            'id': q['id'],
            'title': q['title'],
            'expected_output': q['expected_output'],
            'submitted_code': submitted_code,
            'marks': marks,
            'notes': notes,
            'is_answered': bool(submitted_code and submitted_code.strip())
        })

    return render_template(
        'admin_grade.html',
        applicant=applicant,
        questions=grading_questions,
        total_assigned_marks=total_assigned_marks,
        max_possible_marks=len(QUESTIONS) * 10
    )

@app.route('/admin/save_grade/<int:applicant_id>', methods=['POST'])
def admin_save_grade(applicant_id):
    data = request.get_json() or {}
    marks_dict = data.get('marks', {})
    notes_dict = data.get('notes', {})
    overall_feedback = data.get('overall_feedback', '')
    status = data.get('status', 'Graded')

    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cursor = conn.cursor()

    total_marks = 0.0
    for q_id_str, mark_val in marks_dict.items():
        try:
            q_id = int(q_id_str)
            mark_float = float(mark_val) if mark_val not in (None, '') else 0.0
            note_val = notes_dict.get(q_id_str, '')
            total_marks += mark_float

            cursor.execute('''
                INSERT INTO answers (applicant_id, question_id, marks, notes, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(applicant_id, question_id) DO UPDATE SET
                    marks = excluded.marks,
                    notes = excluded.notes,
                    updated_at = CURRENT_TIMESTAMP
            ''', (applicant_id, q_id, mark_float, note_val))
        except (ValueError, TypeError):
            continue

    # Update applicant total marks and status
    cursor.execute('''
        UPDATE applicants
        SET status = ?,
            total_marks = ?,
            overall_feedback = ?
        WHERE id = ?
    ''', (status, total_marks, overall_feedback, applicant_id))

    conn.commit()
    conn.close()
    return jsonify({
        'status': 'success',
        'message': f'Marks saved successfully! Total: {total_marks}',
        'total_marks': total_marks
    })

@app.route('/admin/delete/<int:applicant_id>', methods=['POST'])
def admin_delete_applicant(applicant_id):
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM answers WHERE applicant_id = ?", (applicant_id,))
    cursor.execute("DELETE FROM applicants WHERE id = ?", (applicant_id,))
    conn.commit()
    conn.close()
    return jsonify({
        'status': 'success',
        'message': f'Applicant #{applicant_id} and all related answers deleted successfully.'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
