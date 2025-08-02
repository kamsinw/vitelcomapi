# Trivia Game API

This is the RESTful API backend for the Trivia Game platform, built using **Flask** and **MongoDB**. It supports both user and admin interfaces, managing authentication, question handling, gameplay logic, and performance tracking for 10,000+ concurrent users.

## 🌟 Features

- RESTful API built with Flask
- Secure admin/user authentication (hashed passwords, session handling)
- Dynamic subject and category creation
- Question CRUD operations
- Randomized question delivery with stat tracking
- MongoDB (NoSQL) for fast and scalable data operations
- CORS-enabled for multi-origin frontend communication

---

## 📁 Directory Structure

trivia-api/
├── app.py # Main application file
├── requirements.txt # Python dependencies


---

## 🧰 Tech Stack

- **Python** + **Flask**
- **MongoDB** via PyMongo
- **Flask-Bcrypt** for password hashing
- **Flask-CORS** for handling cross-origin requests
- **Flask Session** for managing login states

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/trivia-api.git
cd trivia-api

2. Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure MongoDB

Update the connectionString variable in app.py with your actual MongoDB URI:

connectionString = 'mongodb+srv://<username>:<password>@cluster.mongodb.net/'

▶️ Running the App

python app.py

By default, the API runs on:

http://localhost:5001

🔐 Authentication

    Admin Login: /admin/login

    User Login: /user/login

    Both routes use phone/password and maintain session states using Flask sessions.

📫 API Overview
🔒 Admin Endpoints
Method	Endpoint	Description
POST	/admin/signup	Register a new admin
POST	/admin/login	Admin login
GET	/admin/get_subjects	Get all subjects
POST	/admin/subjects	Add new subject
POST	/admin/subjects/categories	Add category to latest subject
GET	/admin/get_categories	Get categories for a subject
POST	/admin/questions	Add a new question
PUT	/admin/questions	Edit a question
GET	/admin/get_questions	Get questions for a category
PUT	/admin/update_subject	Update a subject name
PUT	/admin/update_category	Update a category name
PUT	/admin/update_question	Update question text/answers
👤 User Endpoints
Method	Endpoint	Description
POST	/user/signup	User registration
POST	/user/login	User login
GET	/user/categories/random_question	Get random question from category
POST	/user/answer_question	Submit an answer and update stats
🧪 Testing

You can use Postman, Insomnia, or any HTTP client to test these endpoints.

Recommended flow:

    Sign up/login as admin

    Add subject → add category → add question

    Sign up/login as user

    Fetch random question from a category

    Submit answer and check stats

📌 Notes

    Admins and users are stored in different collections.

    All password data is securely hashed with Bcrypt.

    Session data persists across requests using Flask session.

    The API assumes you are also running separate frontend clients for admin and user (see trivia-ui and trivia-admin).
