import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = create_app().test_client()
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:{}@{}/{}".format('1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_available_categories(self):
        """"Test API to get all categories"""
        response = self.client.get('/api/v1/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data["# of categories"], int)
        self.assertTrue(len(data["categories"]) > 0)
        self.assertEqual(data["success"], True)

    # def test_delete_question_given_id(self):
    #     """"Test API to delete a question"""
    #     response = self.client.delete('/api/v1/questions/9')
    #     data = json.loads(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(data["message"], 'Question deleted successfully.')
    #     self.assertEqual(data["success"], True)

    def test_delete_question_given_wrong_id(self):
        """"Test API to delete a question with non existent id"""
        response = self.client.delete('/api/v1/questions/900')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], 'resource not found')
        self.assertEqual(data["success"], False)


    def test_create_new_question(self):
        """"Test API to add a new question"""
        input_data = {
            "question":"this is a test question",
            "answer":"this is a test answer",
            "difficulty":5,
            "category":2
        }
        response = self.client.post('/api/v1/questions', data= json.dumps(input_data), content_type='application/json', )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["message"], 'New question was added.')
        self.assertEqual(data["success"], True)

    def test_create_new_question_wrong_data_format(self):
        """"Test API to add a new question with wrong data format"""
        input_data = {
            "question":"this is a test question",
            "answer":"this is a test answer",
            "difficulty":"sdfsdf",
            "category":2
        }
        response = self.client.post('/api/v1/questions', data= json.dumps(input_data), content_type='application/json', )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(data["message"], 'Bad input format')
        self.assertEqual(data["success"], False)

    def test_get_questions_basing_on_category(self):
        """"Test API to get questions according to their category"""
        response = self.client.get('/api/categories/5/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data["# of questions"], int)
        self.assertTrue(len(data["questions"]) > 0)
        self.assertEqual(data["success"], True)

    def test_get_questions_basing_on_wrong_category(self):
        """"Test API to get questions according to a wrong category"""
        response = self.client.get('/api/categories/500/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], 'resource not found')
        self.assertEqual(data["success"], False)

    def test_search_term_in_question_found(self):
        """"Test API to search for a question basing on a keyword"""
        search_data = {
            "search":"which"
        }
        response = self.client.post('/api/v1/questions/search', data= json.dumps(search_data), content_type='application/json', )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data["questions"]) > 0)
        self.assertEqual(data["success"], True)
        self.assertIsInstance(data["# of questions"], int)

    def test_search_term_in_question_not_found(self):
        """"Test API to search for a question basing on a wrong keyword"""
        input_data = {
            "search":"sdfasf"
        }
        response = self.client.post('/api/v1/questions/search', data= json.dumps(input_data), content_type='application/json', )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], 'resource not found')
        self.assertEqual(data["success"], False)

    def test_get_next_category_question(self):
        """"Test API to get the next quiz question"""
        response = self.client.get('/api/v1/quiz/3/14')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data["next_question"], object)
        self.assertEqual(data["success"], True)

    def test_get_next_category_question_on_last_category_qn(self):
        """"Test API to get the next quiz question"""
        response = self.client.get('/api/v1/quiz/3/15')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["message"], "No more available questions in category")
        self.assertEqual(data["success"], False)

    def test_get_next_category_question_on_wrong_prev_qn_input(self):
        """"Test API to get the next quiz question with wrong previous question id"""
        response = self.client.get('/api/v1/quiz/3/105')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "resource not found")
        self.assertEqual(data["success"], False)


if __name__ == "__main__":
    unittest.main()