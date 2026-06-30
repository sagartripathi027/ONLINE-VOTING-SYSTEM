🗳️ Online Voting System

A web-based voting system built using Django (backend) and HTML, CSS, JavaScript (frontend) that allows users to register, log in, view candidates, and securely cast votes with a one-user-one-vote restriction.

🚀 Features
User registration and login system
One user can vote only once
Candidate listing and voting
Secure authentication using Django
Admin panel to manage candidates and results
Simple responsive UI using HTML, CSS, JavaScript
🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript
Backend: Django (Python)
Database: SQLite (default) / MySQL (optional)
⚙️ Setup Instructions
git clone https://github.com/your-username/online-voting-system.git
cd online-voting-system
python -m venv venv
venv\Scripts\activate   # Windows
pip install django
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
🗳️ Working Flow
User registers or logs in
Candidate list is displayed
User selects a candidate and votes
System checks if user already voted
Vote is saved in database
Results are updated
🔐 Security
Django authentication system
CSRF protection
One vote per user restriction
👨‍💻 Author

Sagar Tripathi
