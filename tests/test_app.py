import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class EvaluationAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_redirect(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/evaluate/2', res.headers['Location'])

    def test_evaluate_page(self):
        res = self.client.get('/evaluate/2')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Python Evaluation', res.data)
        self.assertIn(b'Applicant ID:', res.data)
        self.assertIn(b'1. Basic : write code to split odd and even in the range of 1 to 10.', res.data)
        self.assertIn(b'Submit All Answers', res.data)

    def test_run_code(self):
        res = self.client.post('/run', data='print("Hello Evaluator")', content_type='text/plain')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Hello Evaluator', res.get_data(as_text=True))

    def test_submit_evaluation(self):
        payload = {
            'applicant_id': 2,
            'answers': {
                '1': 'even = [2, 4, 6, 8, 10]\nodd = [1, 3, 5, 7, 9]\nprint((even, odd))'
            }
        }
        res = self.client.post('/submit_evaluation', json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Answers submitted successfully!', res.get_data(as_text=True))

    def test_register_applicant(self):
        res = self.client.post('/register', json={})
        self.assertEqual(res.status_code, 200)
        self.assertIn('New applicant registered with ID:', res.get_data(as_text=True))

    def test_admin_dashboard(self):
        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Applicant Submissions', res.data)
        self.assertIn(b'Submissions Pipeline', res.data)

    def test_admin_grade_page(self):
        res = self.client.get('/admin/grade/2')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Applicant #2', res.data)
        self.assertIn(b'Marks (out of 10):', res.data)
        self.assertIn(b'Save Marks', res.data)

    def test_admin_save_grade(self):
        grade_payload = {
            'marks': {
                '1': '10',
                '2': '9.5',
                '5': '8'
            },
            'notes': {
                '1': 'Perfect solution',
                '5': 'Fixed class variables'
            },
            'overall_feedback': 'Strong technical skills in Python fundamentals.',
            'status': 'Graded'
        }
        res = self.client.post('/admin/save_grade/2', json=grade_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_marks'], 27.5)

    def test_admin_delete_applicant(self):
        import re
        # Register a temporary applicant to delete
        reg_res = self.client.post('/register', json={})
        self.assertEqual(reg_res.status_code, 200)
        match = re.search(r'ID:\s*(\d+)', reg_res.get_data(as_text=True))
        self.assertIsNotNone(match)
        temp_id = int(match.group(1))

        # Submit answer for temp applicant
        self.client.post('/submit_evaluation', json={
            'applicant_id': temp_id,
            'answers': {'1': 'print("temp")'}
        })

        # Delete applicant
        del_res = self.client.post(f'/admin/delete/{temp_id}')
        self.assertEqual(del_res.status_code, 200)
        del_data = del_res.get_json()
        self.assertEqual(del_data['status'], 'success')
        self.assertIn(f'Applicant #{temp_id}', del_data['message'])

if __name__ == '__main__':
    unittest.main()

