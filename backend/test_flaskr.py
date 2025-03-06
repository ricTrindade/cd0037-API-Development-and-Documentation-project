import json
import os
import unittest

from dotenv import load_dotenv

from flaskr import create_app
from models import db

load_dotenv()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = os.getenv("database_name_test")
        self.database_user = os.getenv("database_user")
        self.database_password = os.getenv("database_password")
        self.database_host = os.getenv("database_host")
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            #db.drop_all()

    # ---- Tests for /categories ----
    def test_get_categories_success(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertTrue(data['success'])
        self.assertIn('categories', data)

    # ---- Tests for /questions ----
    def test_get_questions_success(self):
        res = self.client.get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertTrue(data['success'])
        self.assertIn('questions', data)

    # ---- Tests for /questions/<int:question_id> ----
    def test_delete_question_success(self):
        res = self.client.delete('/questions/10')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_question_not_found(self):
        res = self.client.delete('/questions/999')
        self.assertEqual(res.status_code, 404)

    # ---- Tests for /questions (POST) ----
    def test_submit_question_success(self):
        new_question = {
            "question": "What is 2+2?",
            "answer": "4",
            "difficulty": 1,
            "category": 1
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_submit_question_missing_fields(self):
        new_question = {
            "question": "What is 2+2?",
            "answer": "4"
        }
        res = self.client.post('/questions', json=new_question)
        self.assertEqual(res.status_code, 400)

    # ---- Tests for /questions/search ----
    def test_search_questions_success(self):
        res = self.client.post('/questions/search', json={"searchTerm": "France"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_search_questions_empty_term(self):
        res = self.client.post('/questions/search', json={"searchTerm": ""})
        self.assertEqual(res.status_code, 400)

    # ---- Tests for /categories/<int:category_id>/questions ----
    def test_get_questions_by_category_success(self):
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_questions_by_category_not_found(self):
        res = self.client.get('/categories/999/questions')
        self.assertEqual(res.status_code, 404)

    # ---- Tests for /quizzes ----
    def test_get_next_question_success(self):
        res = self.client.post('/quizzes', json={"previous_questions": [], "quiz_category": {"id": 1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_next_question_invalid_request(self):
        res = self.client.post('/quizzes', json={})
        self.assertEqual(res.status_code, 400)

    # ---- Error Handler Tests ----
    def test_404_error_handler(self):
        res = self.client.get('/nonexistent_route')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_400_error_handler(self):
        res = self.client.post('/questions', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    def test_415_error_handler(self):
        res = self.client.post('/questions', data="")
        self.assertEqual(res.status_code, 415)
        data = json.loads(res.data)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
