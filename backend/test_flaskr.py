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

    def test_get_categories(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('categories', data)

    def test_get_questions_pagination(self):
        res = self.client.get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('questions', data)

    def test_delete_question(self):
        res = self.client.delete('/questions/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_post_question(self):
        new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "difficulty": 2,
            "category": 1
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_search_questions(self):
        res = self.client.post('/questions/search', json={"searchTerm": "Body"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['questions']), 0)

    def test_get_questions_by_category(self):
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['questions']), 0)

    def test_get_next_question(self):
        quiz_data = {
            "previous_questions": [],
            "quiz_category": {"id": 1}
        }
        res = self.client.post('/quizzes', json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('question', data)

    def test_404_get_questions_by_invalid_category(self):
        res = self.client.get('/categories/999/questions')
        self.assertEqual(404, res.status_code)

    def test_400_submit_question_missing_fields(self):
        res = self.client.post('/questions', json={})
        self.assertEqual(res.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
