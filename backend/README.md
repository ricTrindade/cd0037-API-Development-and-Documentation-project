# Trivia API

This is a Flask-based API that serves trivia questions. It allows users to retrieve questions, submit new ones, delete existing ones, and play quizzes.

## Installation and Setup

### Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Install Dependencies

1. Create a virtual environment (optional but recommended):

   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

2. Install required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

### Set Up the Database

1. Run the following command to set up the database:

   ```sh
   flask db upgrade
   ```

2. Populate the database with initial data (if necessary):

   ```sh
   python seed_database.py
   ```

### Running the Server

Start the Flask development server:

```sh
flask run
```

The server will run at `http://127.0.0.1:5000/`.

## API Documentation

### `GET /categories`

- Fetches all available categories.
- **Request Parameters:** None
- **Response Body:**
  ```json
  {
    "success": true,
    "categories": {
      "1": "Science",
      "2": "Art",
      "3": "Geography"
    }
  }
  ```

### `GET /questions?page=<int>`

- Fetches a paginated list of questions (default 10 per page).
- **Request Parameters:**
  - `page` (integer, optional): Page number for pagination.
- **Response Body:**
  ```json
  {
    "success": true,
    "questions": [
      {"id": 1, "question": "What is Python?", "answer": "A programming language"}
    ],
    "totalQuestions": 1,
    "categories": {
      "1": "Science",
      "2": "Art"
    },
    "currentCategory": "Science"
  }
  ```

### `DELETE /questions/<int:question_id>`

- Deletes a question by its ID.
- **Request Parameters:**
  - `question_id` (integer, required): The ID of the question to delete.
- **Response Body:**
  ```json
  {
    "success": true,
    "message": "Question deleted successfully"
  }
  ```

### `POST /questions`

- Creates a new question.
- **Request Body:**
  ```json
  {
    "question": "What is Flask?",
    "answer": "A Python web framework",
    "difficulty": 2,
    "category": 1
  }
  ```
- **Response Body:**
  ```json
  {
    "success": true,
    "message": "Question added successfully",
    "question": {
      "id": 5,
      "question": "What is Flask?",
      "answer": "A Python web framework",
      "difficulty": 2,
      "category": 1
    }
  }
  ```

### `POST /questions/search`

- Searches for questions containing the given term.
- **Request Body:**
  ```json
  {
    "searchTerm": "Python"
  }
  ```
- **Response Body:**
  ```json
  {
    "success": true,
    "questions": [
      {"id": 1, "question": "What is Python?", "answer": "A programming language"}
    ],
    "total_questions": 1,
    "current_category": "Science"
  }
  ```

### `GET /categories/<int:category_id>/questions`

- Retrieves questions for a specific category.
- **Request Parameters:**
  - `category_id` (integer, required): ID of the category.
- **Response Body:**
  ```json
  {
    "success": true,
    "questions": [
      {"id": 1, "question": "What is Python?", "answer": "A programming language"}
    ],
    "total_questions": 1,
    "current_category": "Science"
  }
  ```

### `POST /quizzes`

- Retrieves the next quiz question.
- **Request Body:**
  ```json
  {
    "previous_questions": [1, 2],
    "quiz_category": {"id": 1}
  }
  ```
- **Response Body:**
  ```json
  {
    "success": true,
    "question": {
      "id": 3,
      "question": "What is Flask?",
      "answer": "A Python web framework"
    },
    "force_end": false
  }
  ```

## Error Handling

The API returns the following error responses:

- **400 Bad Request:**

  ```json
  {
    "success": false,
    "message": "bad request"
  }
  ```

- **404 Not Found:**

  ```json
  {
    "success": false,
    "message": "resource not found"
  }
  ```

- **422 Unprocessable Entity:**

  ```json
  {
    "success": false,
    "message": "unprocessable"
  }
  ```

- **500 Internal Server Error:**

  ```json
  {
    "success": false,
    "message": "server Error"
  }
  ```

## Testing

To run unit tests, use:

```sh
pytest
```

