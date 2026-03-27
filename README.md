# 📚 Digital Library App

A full-stack Flask web application to manage books and authors, enhanced with AI-powered book recommendations via RapidAPI.

---

## 🚀 Features

* 📖 Add and manage authors
* 📚 Add books with ISBN, publication year, and rating
* 🔎 Search books by title, author, or ISBN
* ↕️ Sort books by title, author, or rating
* ❌ Delete books and authors (with cascade behavior)
* 🧠 AI-powered book recommendations based on your library
* 🎨 Clean and responsive UI

---

## 🛠️ Tech Stack

* **Backend:** Flask, Flask-SQLAlchemy
* **Database:** SQLite
* **Frontend:** HTML, CSS (Jinja2 Templates)
* **API Integration:** RapidAPI (chatgpt-42)
* **Environment Management:** python-dotenv

---

## 📂 Project Structure

```
project/
│
├── app.py
├── data_models.py
├── requirements.txt
├── .env (not included in repo)
├── data/
│   └── library.sqlite
│
├── templates/
│   ├── home.html
│   ├── add_author.html
│   ├── add_book.html
│   ├── book_detail.html
│   ├── author_detail.html
│   └── recommendation.html
│
└── static/
    └── style.css
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/digital-library.git
cd digital-library
```

---

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env` file

Create a file named `.env` in the root directory:

```
RAPIDAPI_KEY=your_api_key_here
SECRET_KEY=your_secret_key
```

---

### 5. Run the application

```bash
python3 app.py
```

App will be available at:

```
http://localhost:5002
```

---

## 🔑 API Setup (RapidAPI)

This project uses the **chatgpt-42 API** via RapidAPI.

### Steps:

1. Go to RapidAPI
2. Subscribe to the API
3. Copy your API key
4. Add it to your `.env` file

---

## 🧠 AI Recommendation Feature

The app sends your library data (books, authors, ratings) to an AI model which:

* Analyzes your reading preferences
* Suggests 3 new books
* Provides short explanations

---

## ⚠️ Security Notes

* `.env` is excluded via `.gitignore`
* API keys are never stored in code
* SQLite database is local only

---

## 📌 Future Improvements

* User authentication (login system)
* Cloud deployment (AWS / Docker)
* Better UI/UX (React or Tailwind)
* Book cover fallback handling
* Pagination for large libraries

---

## 👨‍💻 Author

Developed by **Sinan**
Background: Electronics Technician → AI Engineering

---

## ⭐ Why this project?

This project demonstrates:

* Full-stack development with Flask
* Database design with relationships
* External API integration
* Clean project structure
* Real-world application logic

---

## 📄 License

This project is for educational and portfolio purposes.
