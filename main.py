from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
import traceback

connectionString = 'mongodb+srv://kamz1022:az52h8uYbNUBzf2@cluster0.p14ijhc.mongodb.net/'
#user: program_permission
#password: 8K3EDCpq8xHeLcnQ
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key'

client = MongoClient(connectionString)
db = client['vitelcomapi']
collection = db['admin_interface']
subjects_collection = db['subjects']
categories_collection = db['categories']
questions_collection = db['questions']
users_collection = db['users']


#######################ADMIN ROUTES##############
@app.route('/admin/signup', methods=['POST'])
def signup():
    data = request.get_json()
    phone = data['phone']
    password = data['password']

    if collection.admins.find_one({'phone': phone}):
        return jsonify({"message": "Phone number already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    collection.admins.insert_one({
        'phone': phone, 
        'password_hash': hashed_password,
        'is_admin': True
    })
    return jsonify({"message": "Admin created successfully"}), 201
#helper function to check admin credentials

# def authenticate_admin(phone, passwords):
#     user.collection.users.find_one({'phone': phone})
#     if user and bcrypt.check_password_hash(user['password_has'],pasword) and user['is_admin']:
#         return True
#     return False
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    phone = data['phone']
    password = data['password']
    
    user = collection.admins.find_one({'phone': phone})
    if user and bcrypt.check_password_hash(user['password_hash'], password) and user['is_admin']:
        session['user_phone'] = phone
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/test', methods=['POST'])
def test():
    return jsonify({'message': 'Login successful'}), 200

@app.route('/admin/get_subjects', methods=['GET'])
def get_subjects():
    subjects = list(collection.find({}))
    for subject in subjects:
        subject['_id'] = str(subject['_id'])
    return jsonify(subjects), 200


@app.route('/admin/subjects', methods=['POST'])
def add_subject():
    # user_phone = session.get('user_phone')
    # if not user_phone:
    #     return jsonify({'message': 'Authentication required'}), 401

    # user = collection.find_one({'phone': user_phone})
    # if not user or not user.get('is_admin'):
    #     return jsonify({'message': 'Admin privileges required'}), 403

    data = request.get_json()
    subject = {'subject_name': data['subject_name']}
    result = collection.insert_one(subject)
    return jsonify({'message': 'Subject added', 'id': str(result.inserted_id)}), 201

@app.route('/admin/subjects/categories', methods=['POST'])
def add_category():
    # user_phone = session.get('user_phone')
    # if not user_phone:
    #     return jsonify({'message': 'Authentication required'}), 401

    # user = collection.find_one({'phone': user_phone})
    # if not user or not user.get('is_admin'):
    #     return jsonify({'message': 'Admin privileges required'}), 403
    data = request.get_json()
    last_subject = collection.find_one({}, sort=[('_id', -1)])  # Fetch the last created subject

    if not last_subject:
        return jsonify({'message': 'No subjects available'}), 400

    category = {'category_name': data['category_name'], 'subject_id': last_subject['_id']}
    result = collection.categories.insert_one(category)
    return jsonify({'message': 'Category added', 'id': str(result.inserted_id)}), 201
@app.route('/admin/get_categories/', methods=['GET'])
def get_categories():
    subject_id = request.args.get('subject_id')
    categories = list(collection.categories.find({'subject_id': ObjectId(subject_id)}))
    for category in categories:
        category['_id'] = str(category['_id'])
        category['subject_id'] = str(category['subject_id'])
    return jsonify(categories), 200


@app.route('/admin/questions', methods=['POST', 'PUT'])
def add_edit_question():
    data = request.get_json()
    category_id = data.get('category_id')
    last_category = collection.categories.find_one({}, sort=[('_id', -1)])  # Fetch the last created category
    category_id = last_category['_id']

    question = {
        'question_text': data['question_text'],
        'answer_choices': data['answer_choices'],
        'correct_answer': data['correct_answer'],
        'difficulty': data['difficulty'],
        'category_id': ObjectId(category_id),
        'is_online': data['is_online']
    }

    if request.method == 'POST':
        result = questions_collection.insert_one(question)
        return jsonify({'message': 'Question added', 'id': str(result.inserted_id)}), 201
    elif request.method == 'PUT':
        question_id = data['_id']
        questions_collection.update_one({'_id': ObjectId(question_id)}, {'$set': question})
        return jsonify({'message': 'Question updated'}), 200
@app.route('/admin/get_questions', methods=['GET'])
def get_questions():
    category_id = request.args.get('catergory_id')
    questions = list(questions_collection.find({'category_id': ObjectId(category_id)}))
    for question in questions:
        question['_id'] = str(question['_id'])
        question['category_id'] = str(question['category_id'])
    return jsonify(questions), 200

# Update a subject
@app.route('/admin/update_subject', methods=['PUT'])
def update_subject():
    data = request.get_json()
    subject_id = data['subject_id']
    new_name = data.get('subject_name')

    if not subject_id or not new_name:
        return jsonify({'message': 'Missing subject ID or new name.'}), 400

    subjects_collection.update_one(
        {'_id': ObjectId(subject_id)},
        {'$set': {'subject_name': new_name}}
    )

    return jsonify({'message': 'Subject updated successfully.'})

# Update a category
@app.route('/admin/update_category', methods=['PUT'])
def update_category():
    data = request.get_json()
    category_id = data['category_id']
    new_name = data.get('category_name')

    if not category_id or not new_name:
        return jsonify({'message': 'Missing category ID or new name.'}), 400

    categories_collection.update_one(
        {'_id': ObjectId(category_id)},
        {'$set': {'category_name': new_name}}
    )

    return jsonify({'message': 'Category updated successfully.'})

# Update a question
@app.route('/admin/update_question', methods=['PUT'])
def update_question():
    data = request.get_json()
    question_id = data['question_id']
    new_question_text = data.get('question')
    new_answers = data.get('answers')
    new_correct_answer = data.get('correct_answer')

    if not question_id:
        return jsonify({'message': 'Missing question ID.'}), 400

    update_fields = {}
    if new_question_text:
        update_fields['question'] = new_question_text
    if new_answers:
        update_fields['answers'] = new_answers
    if new_correct_answer:
        update_fields['correct_answer'] = new_correct_answer

    questions_collection.update_one(
        {'_id': ObjectId(question_id)},
        {'$set': update_fields}
    )

    return jsonify({'message': 'Question updated successfully.'})
#################################USER ROUTES################################
@app.route('/user/signup', methods=['POST'])
def user_signup():
    data = request.get_json()
    phone = data['phone']
    password = data['password']
    
    if users_collection.find_one({'phone': phone}):
        return jsonify({"message": "Phone number already exists"}), 400

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


@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    phone = data['phone']
    password = data['password']
    
    user = users_collection.find_one({'phone': phone})
    
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        session['user_phone'] = phone
        return jsonify({'message': 'Login successful', 'user_phone':session.get('user_phone')}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/user/categories/random_question', methods=['GET'])
def get_random_question():
    category_id = request.args.get('category_id')
    questions = list(questions_collection.find({'category_id': ObjectId(category_id)}))
    questions = list(questions_collection.find({'category_id': ObjectId(category_id)}))
    if not questions:
        return jsonify({'message': 'No questions available for this category'}), 404

    random_question = random.choice(questions)
    answer_choices = random_question['answer_choices']
    #formatted_answers = f"A.) {answer_choices[0]} B.) {answer_choices[1]} C.) {answer_choices[2]} D.) {answer_choices[3]}"
    
    return jsonify({
        'question': random_question['question_text'],
        'answers': answer_choices,
        'id': str(random_question['_id'])
    }), 200
@app.route('/user/answer_question', methods=['POST'])
def answer_question():
    data = request.get_json()
    question_id = data['question_id']
    selected_answer = data['selected_answer']
    phone = session.get('user_phone')

    # user = users_collection.find_one({'phone': phone})
    # if not user:
    #     return jsonify({'message': 'User not found'}), 404

    question = questions_collection.find_one({'_id': ObjectId(question_id)})

    if not question:
        return jsonify({'message': 'Invalid question ID'}), 400

    correct_answer = question['correct_answer']
    user_answered_correctly = correct_answer == selected_answer

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
    app.run(debug=True, port=5001)