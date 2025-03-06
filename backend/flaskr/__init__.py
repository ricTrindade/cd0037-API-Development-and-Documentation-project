from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    CORS(app, resources={"*": {"origins": "*"}})

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    with app.app_context():
        db.create_all()

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():

        # Query all categories from the database
        categories = Category.query.all()

        # Convert categories into the required dictionary format
        categories_dict = {c.id: c.type for c in categories}

        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    # TODO: Front-End does not seem to render the page numbers, need to investigate
    @app.route('/questions')
    def show_questions():

        # Get info from request
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # Fetch Info from DB
        questions = Question.query.all()
        categories = Category.query.all()

        # Format Data
        questions_list = [q.format() for q in questions][start:end]

        return jsonify({
            'success': True,
            'questions': questions_list,
            'totalQuestions': len(questions_list),
            'categories': {c.id: c.type for c in categories},
            'currentCategory': Category.query.order_by('id').first().type if categories else None
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        # Find the question by its ID
        question = Question.query.get_or_404(question_id)

        # Delete the question from the database
        try:
            db.session.delete(question)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Question deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            abort(500)

    @app.route('/questions', methods=['POST'])
    def submit_question():

        # Get the data from the request
        data = request.get_json()
        question_text = data.get('question')
        answer = data.get('answer')
        difficulty = data.get('difficulty')
        category_id = data.get('category')

        # Validate the data
        if not question_text or not answer or not difficulty or not category_id:
            abort(400)

        # Find the category from the database
        category = Category.query.get(category_id)

        # If category doesn't exist, return an error
        if not category:
            abort(404)

        # Create a new question
        new_question = Question(
            question=question_text,
            answer=answer,
            difficulty=difficulty,
            category=category_id
        )

        # Add the question to the database and commit
        try:
            db.session.add(new_question)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Question added successfully',
                'question': new_question.format()
            })
        except Exception as e:
            db.session.rollback()
            print(e)
            abort(500)

    # TODO: Include Pagination Here
    @app.route('/questions/search', methods=['POST'])
    def search_questions():

        # Get the data from the request
        data = request.get_json()
        search_term = data.get('searchTerm', '').strip() # TODO: Decide if this is needed

        # If no search term is provided, return all questions
        if not search_term:
            abort(400)

        # Query the database for questions matching the search term
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')
        ).all()

        # If Nothing found
        if len(questions) == 0:
            return jsonify({
                'success': True,
                'questions': [],
                'total_questions': 0,
                'current_category': ''
            })

        # Format the questions for the response
        questions_data = [q.format() for q in questions]

        return jsonify({
            'success': True,
            'questions': questions_data,
            'total_questions': len(questions_data),
            'current_category': Category.query.get(questions[0].id)
        })

   # TODO: Include Pagination Here
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        # Find the category by ID
        category = Category.query.get_or_404(category_id)

        # Fetch questions associated with this category
        questions = Question.query.filter_by(category=category_id).all()

        return jsonify({
            'success': True,
            'questions': [q.format() for q in questions],
            'total_questions': len(questions),
            'current_category': category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def get_next_question():

        # Get the data from the request
        data = request.get_json()
        previous_questions = data.get('previous_questions', [])
        quiz_category = data.get('quiz_category', {})

        # Validate quiz_category
        category_id = quiz_category.get('id')

        if category_id == 0:
            query_filter = True  # No category filter, fetch from all categories
        elif category_id:
            query_filter = (Question.category == category_id)
        else:
            abort(400)

        # TODO: Verify the code below for ALL(id=0)
        questions = Question.query.filter(
            query_filter,
            ~Question.id.in_(previous_questions)
        ).order_by(Question.id).all()

        # If no more questions are available, end the quiz
        if not questions:
            return jsonify({
                'success' : True,
                'question': None,
                'force_end': True
            })

        # Get the next question (first in the ordered list)
        next_question = questions[0]

        return jsonify({
            'success' : True,
            'question': next_question.format(),  # Assuming your Question model has a format() method
            'force_end': False
        })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(415)
    def unsupported_media_type(error):
        return jsonify({
            'success': False,
            'message': 'Unsupported Media Type'
        }), 415

    @app.errorhandler(400)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'message': 'bad request'
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'message': 'server Error'
        }), 500

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            'success': False,
            'message': 'resource not found'
        }), 404

    return app

if __name__ == '__main__':
   create_app().run(host="0.0.0.0", port=5000)
   print('code changes')