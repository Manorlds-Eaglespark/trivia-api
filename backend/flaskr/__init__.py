import os
from flask import Flask, request, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/api/v1/categories')
    def get_categories():
      categories = Category.query.all()
      if categories:
        format_categories = [Category.format(item) for item in categories]
        return jsonify({
          'success': True,
          'status': 200,
          '# of categories': len(format_categories),
          'categories': format_categories})
      else:
        abort(404)

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/api/v1/questions', methods=['GET'])
    def get_quetions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        categories = Category.query.all()
        format_questions = [Question.format(question) for question in questions]
        format_categories = [Category.format(item) for item in categories]
        return jsonify({
          'questions': format_questions[start:end],
          "# of questions": len(format_questions),
          "categories": format_categories
          })
      
    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/api/v1/questions/<int:id>', methods=['GET','DELETE'])
    def work_on_question(id):
      question = Question.query.get(id)
      if question:
        if request.method == 'GET':
          return jsonify({'question': Question.format(question)})

        if request.method == 'DELETE':
          question.delete()
          return jsonify({
            'success': True,
            'status':200,
            'message': 'Question deleted successfully.'
          }), 200
      else:
        abort(404)

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/api/v1/questions', methods=['POST'])
    def create_new_question():
      question = request.get_json().get('question')
      answer = request.get_json().get('answer')
      category = request.get_json().get('category')
      difficulty = request.get_json().get('difficulty')

      if not (question and answer and\
         category and difficulty) or not isinstance(question, str)\
           or not isinstance(answer, str) or not isinstance(category, int)\
             or not isinstance(difficulty, int):
        abort(406)

      new_question = Question(question, answer, category, difficulty)
      new_question.insert()
      return jsonify({
        "message": "New question was added.",
        "status": 201,
        "success": True
      }),201

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/api/v1/questions/search', methods=['POST'])
    def get_search_question():
      search_query = request.get_json().get('search')
      questions = Question.query.filter(Question.question.ilike("%" + search_query + "%")).all()
      format_qn = [Question.format(qn) for qn in questions]
      if format_qn:
        return jsonify({
          'success':True,
          'status':200,
          '# of questions': len(format_qn),
          'questions': format_qn})
      else:
        abort(404)

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  
    @app.route('/api/categories/<int:id>/questions')
    def get_category_questions(id):
      questions = Question.query.filter_by(category=id).all()
      if questions:
        format_qn = [Question.format(qn) for qn in questions]
        return jsonify({
          'success': True,
          'status':200,
          '# of questions': len(format_qn),
          'questions': format_qn})
      else:
        abort(404)

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/api/v1/quiz/<int:category_id>/<int:prev_qn_id>')
    def get_next_quiz_question(category_id, prev_qn_id):
      questions = Question.query.filter_by(category=category_id).all()
      previous_question = Question.query.get(prev_qn_id)
      if questions and previous_question:
        format_questions = [Question.format(item) for item in questions]
        prev_qn = Question.format(previous_question)
        if (prev_qn["category"] == category_id):
          prv_qn_idx = format_questions.index(prev_qn)
          if prv_qn_idx >= (len(format_questions)-1):
            return jsonify({
              "status": 400,
              "success": False,
              "message":"No more available questions in category"
            }), 400
          else:
            next_qn = format_questions[prv_qn_idx+1]
            return jsonify({
                            'success': True,
                            'status':200,
                            'next_question': next_qn,
                            })
        else:
          abort(400)
      else:
        abort(404)
    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
      }), 404

    @app.errorhandler(422)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable'
      }), 422

    @app.errorhandler(400)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
      }), 400

    @app.errorhandler(406)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 406,
        'message': 'Bad input format'
      }), 406

    @app.errorhandler(500)
    def internal_error(error):
      return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal System Error'
      }), 500

    return app
