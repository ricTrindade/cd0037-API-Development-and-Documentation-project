from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    cors = CORS(app)
    #cors = CORS(app, resources={"*": {"origins": "*"}})

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def show_questions():
        return jsonify({
            'questions': [
                {'id': 1, 'question': 'Test question?', 'category': 'Science', 'difficulty': 2},
                {'id': 2, 'question': 'Another question?', 'category': 'History', 'difficulty': 3}
            ],
            'totalQuestions': 2,
            'categories': {
                'Science': 'Science',
                'History': 'History'
            },
            'currentCategory': 'Science',  # Ensure this is a valid category
        })

    '''
    I am not sure if there's already a comment for this code
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = {
            1: "Science",
            2: "History",
            3: "Math",
            4: "Literature",
            5: "Technology"
        }

        return jsonify({
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<string:category_name>/questions', methods=['GET'])
    def get_questions_by_category(category_name):
        # Sample data for categories and questions
        categories = {
            "Science": 1,
            "History": 2,
            "Math": 3,
            "Literature": 4,
            "Technology": 5
        }

        questions_data = {
            "Science": [
                {'id': 1, 'question': 'What is the chemical symbol for water?', 'category': 'Science'},
                {'id': 2, 'question': 'What is the speed of light?', 'category': 'Science'}
            ],
            "History": [
                {'id': 3, 'question': 'Who discovered America?', 'category': 'History'},
                {'id': 4, 'question': 'What year did WWII end?', 'category': 'History'}
            ]
            # Add more categories and questions as needed
        }

        # Check if the category exists
        if category_name not in categories:
            return jsonify({'error': 'Category not found'}), 404

        # Get the questions for the specified category
        questions = questions_data.get(category_name, [])

        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'current_category': category_name
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

if __name__ == '__main__':
   create_app().run(host="0.0.0.0", port=5000)
   print('code changes')