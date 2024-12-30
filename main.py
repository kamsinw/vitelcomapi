from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
import traceback

# MongoDB connection string
connectionString = 'mongodb+srv://kamz1022:az52h8uYbNUBzf2@cluster0.p14ijhc.mongodb.net/'

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes
bcrypt = Bcrypt(app)  # For password hashing
app.secret_key = 'your_secret_key'  # Secret key for session management

# Initialize MongoDB client and select database and collections
client = MongoClient(connectionString)
db = client['vitelcomapi']
collection = db['admin_interface']  # This is probably used for multiple purposes
subjects_collection = db['subjects']
categories_collection = db['categories']
questions_collection = db['questions']
users_collection = db['users']

####################### ADMIN ROUTES ######################

# Route for admin signup
@app.route('/admin/signup', methods=['POST'])
def signup():
    data = request.get_json()  # Get JSON data from request
    phone = data['phone']
    password = data['password']

    # Check if the phone number already exists
    if collection.admins.find_one({'phone': phone}):
        return jsonify({"message": "Phone number already exists"}), 400

    # Hash the password and insert the admin into the database
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    collection.admins.insert_one({
        'phone': phone, 
        'password_hash': hashed_password,
        'is_admin': True
    })
    return jsonify({"message": "Admin created successfully"}), 201

# Route for admin login
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()  # Get JSON data from request
    phone = data['phone']
    password = data['password']
    
    # Find the admin by phone number
    user = collection.admins.find_one({'phone': phone})
    # Check if the user exists, password is correct, and user is an admin
    if user and bcrypt.check_password_hash(user['password_hash'], password) and user['is_admin']:
        session['user_phone'] = phone  # Store the phone number in the session
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401  # Return 401 for unauthorized access

# Route for testing (example placeholder route)
@app.route('/test', methods=['POST'])
def test():
    return jsonify({'message': 'Login successful'}), 200

# Route to get all subjects
@app.route('/admin/get_subjects', methods=['GET'])
def get_subjects():
    subjects = list(collection.find({}))  # Find all subjects
    for subject in subjects:
        subject['_id'] = str(subject['_id'])  # Convert ObjectId to string
    return jsonify(subjects), 200

# Route to add a new subject
@app.route('/admin/subjects', methods=['POST'])
def add_subject():
    data = request.get_json()  # Get JSON data from request
    subject = {'subject_name': data['subject_name']}
    result = collection.insert_one(subject)  # Insert the subject into the database
    return jsonify({'message': 'Subject added', 'id': str(result.inserted_id)}), 201

# Route to add a new category to the last created subject
@app.route('/admin/subjects/categories', methods=['POST'])
def add_category():
    data = request.get_json()  # Get JSON data from request
    last_subject = collection.find_one({}, sort=[('_id', -1)])  # Fetch the last created subject

    if not last_subject:
        return jsonify({'message': 'No subjects available'}), 400

    category = {'category_name': data['category_name'], 'subject_id': last_subject['_id']}
    result = collection.categories.insert_one(category)  # Insert the category into the database
    return jsonify({'message': 'Category added', 'id': str(result.inserted_id)}), 201

# Route to get categories for a specific subject
@app.route('/admin/get_categories/', methods=['GET'])
def get_categories():
    subject_id = request.args.get('subject_id')  # Get subject ID from query parameters
    categories = list(collection.categories.find({'subject_id': ObjectId(subject_id)}))  # Find categories by subject ID
    for category in categories:
        category['_id'] = str(category['_id'])  # Convert ObjectId to string
        category['subject_id'] = str(category['subject_id'])  # Convert ObjectId to string
    return jsonify(categories), 200

# Route to add or edit a question
@app.route('/admin/questions', methods=['POST', 'PUT'])
def add_edit_question():
    data = request.get_json()  # Get JSON data from request
    last_category = collection.categories.find_one({}, sort=[('_id', -1)])  # Fetch the last created category
    category_id = last_category['_id']  # Get the last category's ID

    # Prepare the question data
    question = {
        'question_text': data['question_text'],
        'answer_choices': data['answer_choices'],
        'correct_answer': data['correct_answer'],
        'difficulty': data['difficulty'],
        'category_id': ObjectId(category_id),
        'is_online': data['is_online']
    }

    if request.method == 'POST':
        result = questions_collection.insert_one(question)  # Insert the question into the database
        return jsonify({'message': 'Question added', 'id': str(result.inserted_id)}), 201
    elif request.method == 'PUT':
        question_id = data['_id']  # Get the question ID
        questions_collection.update_one({'_id': ObjectId(question_id)}, {'$set': question})  # Update the question
        return jsonify({'message': 'Question updated'}), 200

# Route to get questions for a specific category
@app.route('/admin/get_questions', methods=['GET'])
def get_questions():
    category_id = request.args.get('catergory_id')  # Get category ID from query parameters
    questions = list(questions_collection.find({'category_id': ObjectId(category_id)}))  # Find questions by category ID
    for question in questions:
        question['_id'] = str(question['_id'])  # Convert ObjectId to string
        question['category_id'] = str(question['category_id'])  # Convert ObjectId to string
    return jsonify(questions), 200

# Route to update a subject
@app.route('/admin/update_subject', methods=['PUT'])
def update_subject():
    data = request.get_json()  # Get JSON data from request
    subject_id = data['subject_id']
    new_name = data.get('subject_name')

    if not subject_id or not new_name:
        return jsonify({'message': 'Missing subject ID or new name.'}), 400

    # Update the subject name in the database
    subjects_collection.update_one(
        {'_id': ObjectId(subject_id)},
        {'$set': {'subject_name': new_name}}
    )

    return jsonify({'message': 'Subject updated successfully.'})

# Route to update a category
@app.route('/admin/update_category', methods=['PUT'])
def update_category():
    data = request.get_json()  # Get JSON data from request
    category_id = data['category_id']
    new_name = data.get('category_name')

    if not category_id or not new_name:
        return jsonify({'message': 'Missing category ID or new name.'}), 400

    # Update the category name in the database
    categories_collection.update_one(
        {'_id': ObjectId(category_id)},
        {'$set': {'category_name': new_name}}
    )

    return jsonify({'message': 'Category updated successfully.'})

# Route to update a question
@app.route('/admin/update_question', methods=['PUT'])
def update_question():
    data = request.get_json()  # Get JSON data from request
    question_id = data['question_id']
    new_question_text = data.get('question')
    new_answers = data.get('answers')
    new_correct_answer = data.get('correct_answer')

    if not question_id:
        return jsonify({'message': 'Missing question ID.'}), 400

    # Prepare the fields to update
    update_fields = {}
    if new_question_text:
        update_fields['question'] = new_question_text
    if new_answers:
        update_fields['answers'] = new_answers
    if new_correct_answer:
        update_fields['correct_answer'] = new_correct_answer

    # Update the question in the database
    questions_collection.update_one(
        {'_id': ObjectId(question_id)},
        {'$set': update_fields}
    )

    return jsonify({'message': 'Question updated successfully.'})

######################## USER ROUTES ########################

# Route for user signup
@app.route('/user/signup', methods=['POST'])
def user_signup():
    data = request.get_json()  # Get JSON data from request
    phone = data['phone']
    password = data['password']
    
    # Check if the phone number already exists
    if users_collection.find_one({'phone': phone}):
        return jsonify({"message": "Phone number already exists"}), 400

    # Hash the password and insert the user into the database
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users_collection.insert_one({
        'phone': phone,
        'password_hash': hashed_password,
        'total_correct': 0,
        'total_answered': 0,
        'encountered_questions': [],
        'is_admin': False
    })
    return jsonify({"message": "User created successfully"}), 201

# Route for user login
@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.get_json()  # Get JSON data from request
    phone = data['phone']
    password = data['password']
    
    # Find the user by phone number
    user = users_collection.find_one({'phone': phone})
    
    # Check if the user exists and the password is correct
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        session['user_phone'] = phone  # Store the phone number in the session
        return jsonify({'message': 'Login successful', 'user_phone':session.get('user_phone')}), 200
    return jsonify({'message': 'Invalid credentials'}), 401  # Return 401 for unauthorized access

# Route to get a random question from a category
@app.route('/user/categories/random_question', methods=['GET'])
def get_random_question():
    category_id = request.args.get('category_id')  # Get category ID from query parameters
    questions = list(questions_collection.find({'category_id': ObjectId(category_id)}))  # Find questions by category ID
    
    if not questions:
        return jsonify({'message': 'No questions available for this category'}), 404  # Return 404 if no questions found

    random_question = random.choice(questions)  # Select a random question
    answer_choices = random_question['answer_choices']
    
    return jsonify({
        'question': random_question['question_text'],
        'answers': answer_choices,
        'id': str(random_question['_id'])
    }), 200

# Route to submit an answer to a question
@app.route('/user/answer_question', methods=['POST'])
def answer_question():
    data = request.get_json()  # Get JSON data from request
    question_id = data['question_id']
    selected_answer = data['selected_answer']
    phone = session.get('user_phone')  # Get the user's phone number from the session

    question = questions_collection.find_one({'_id': ObjectId(question_id)})  # Find the question by ID

    if not question:
        return jsonify({'message': 'Invalid question ID'}), 400  # Return 400 if question not found

    correct_answer = question['correct_answer']
    user_answered_correctly = correct_answer == selected_answer  # Check if the user's answer is correct

    # Update the user's statistics in the database
    users_collection.update_one(
        {'phone': phone},
        {
            '$inc': {
                'total_answered': 1,
                'total_correct': 1 if user_answered_correctly else 0
            },
            '$addToSet': {'encountered_questions': str(question_id)}
        }
    )

    result_message = 'Correct!' if user_answered_correctly else f'Incorrect, the correct answer is {correct_answer}'

    return jsonify({
        'message': result_message,
        'correct': user_answered_correctly
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Run the Flask application on port 5001 with debug mode enabled
