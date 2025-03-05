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

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    with app.app_context():
        db.create_all()

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # TODO: CHECK IF PAGINATION IS NEEDED
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # Query all categories from the database
        categories = Category.query.all()

        # Convert categories into the required dictionary format
        categories_dict = {c.id: c.type for c in categories}

        return jsonify({
            'categories': categories_dict
        })


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
    # TODO: IMPLEMENT PAGINATION
    @app.route('/questions')
    def show_questions():
        questions = Question.query.all()
        categories = Category.query.all()

        return jsonify({
            'questions': [q.format() for q in questions],
            'totalQuestions': len(questions),
            'categories': {c.id: c.type for c in categories},
            'currentCategory': Category.query.order_by('id').first().type if categories else None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # Find the question by its ID
        question = Question.query.get(question_id)

        # If the question doesn't exist, return a 404 error
        if not question:
            return jsonify({'error': 'Question not found'}), 404

        # Delete the question from the database
        try:
            db.session.delete(question)
            db.session.commit()
            return jsonify({'message': 'Question deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def submit_question():
        # Get the data from the request
        data = request.get_json()

        # Extract individual fields
        question_text = data.get('question')
        answer = data.get('answer')
        difficulty = data.get('difficulty')
        category_id = data.get('category')

        # Validate the data
        if not question_text or not answer or not difficulty or not category_id:
            return jsonify({'error': 'Missing required fields'}), 400

        # Find the category from the database
        category = Category.query.get(category_id)

        # If category doesn't exist, return an error
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        # Create a new question
        new_question = Question(
            question=question_text,
            answer=answer,
            difficulty=difficulty,
            category=category_id  # assuming category_id is passed as the foreign key
        )

        # Add the question to the database and commit
        try:
            db.session.add(new_question)
            db.session.commit()
            return jsonify({'message': 'Question added successfully', 'question': new_question.format()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        data = request.get_json()

        # Extract search term from the request data
        search_term = data.get('searchTerm', '').strip()

        # If no search term is provided, return all questions
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400

        # Query the database for questions matching the search term (case insensitive)
        questions = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')  # Using ILIKE for case-insensitive search
        ).all()

        # Format the questions for the response
        questions_data = [q.format() for q in questions]

        return jsonify({
            'questions': questions_data,
            'total_questions': len(questions_data),
            'current_category': 'All Categories',  # Or get the category if needed
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        # Find the category by ID
        category = Category.query.get_or_404(category_id)

        # Fetch questions associated with this category
        questions = Question.query.filter_by(category=category_id).all()

        return jsonify({
            'questions': [q.format() for q in questions],
            'total_questions': len(questions),
            'current_category': category.type
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
    @app.route('/quizzes', methods=['POST'])
    def get_next_question():
        data = request.get_json()

        # Extract previous questions and quiz category from request data
        previous_questions = data.get('previous_questions', [])
        quiz_category = data.get('quiz_category', {})

        # Validate quiz_category
        category_id = quiz_category.get('id')

        if category_id == 0:
            query_filter = True  # No category filter, fetch from all categories
        elif category_id:
            query_filter = (Question.category == category_id)
        else:
            return jsonify({'error': 'Invalid category'}), 400

        # TODO: Verify the code below for ALL(id=0)
        questions = Question.query.filter(
            query_filter,
            ~Question.id.in_(previous_questions)
        ).order_by(Question.id).all()

        # If no more questions are available, end the quiz
        if not questions:
            return jsonify({'question': None, 'force_end': True})

        # Get the next question (first in the ordered list)
        next_question = questions[0]

        return jsonify({
            'question': next_question.format(),  # Assuming your Question model has a format() method
            'force_end': False
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

if __name__ == '__main__':
   create_app().run(host="0.0.0.0", port=5000)
   print('code changes')