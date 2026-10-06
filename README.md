# Library Management System - Python + MongoDB

## Requirements
- Python 3.10+
- MongoDB Community Server running locally
- Tkinter (normally included with Python on Windows)

## Installation

1. Install and start MongoDB.
2. Open this project in VS Code.
3. Open Terminal in the project folder.
4. Run:

```bash
pip install -r requirements.txt
python main.py
```

## Login
Username: `admin`
Password: `admin123`

## Database
The application automatically creates:

- LibraryDB
- admins
- books
- students
- issued_books

## Fine
Fine is calculated at ₹5 per day after the 14-day due period.

## Notes
The MongoDB connection uses:
mongodb://localhost:27017/

If MongoDB is running on another host/port, change MONGO_URI in database.py.
