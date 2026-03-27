import os
from datetime import datetime

import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"

basedir = os.path.abspath(os.path.dirname(__file__))
database_dir = os.path.join(basedir, "data")
database_path = os.path.join(database_dir, "library.sqlite")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def parse_date(date_string):
    """
    Convert a YYYY-MM-DD string into a date object.

    Args:
        date_string (str): Raw date string from the form.

    Returns:
        date | None: Parsed date or None if empty.
    """
    if not date_string:
        return None
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def generate_ai_recommendation(books):
    """
    Generate book recommendations using the RapidAPI chatgpt-42 endpoint.

    Args:
        books (list[Book]): Books stored in the database.

    Returns:
        str: Recommendation text or error message.
    """
    if not books:
        return "Keine Bücher vorhanden."

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        return "RAPIDAPI_KEY fehlt."

    library_text = "\n".join(
        [
            (
                f"- Titel: {book.title}, "
                f"Autor: {book.author.name}, "
                f"Jahr: {book.publication_year if book.publication_year else 'unbekannt'}, "
                f"Bewertung: {book.rating if book.rating is not None else 'keine'}"
            )
            for book in books
        ]
    )

    prompt = f"""
Ich habe diese Bücher in meiner Bibliothek:
{library_text}

Empfiehl mir genau 3 neue Bücher, die gut dazu passen.
Begründe jede Empfehlung kurz.
Antworte auf Deutsch.
"""

    url = "https://chatgpt-42.p.rapidapi.com/conversationgpt4"
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "chatgpt-42.p.rapidapi.com"
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "system_prompt": "",
        "temperature": 0.7,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 512,
        "web_access": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "result" in data:
            return data["result"]

        return f"Unbekanntes Antwortformat: {data}"

    except requests.RequestException as error:
        return f"Fehler bei der RapidAPI-Anfrage: {error}"


@app.route("/")
def home():
    """
    Display the homepage with all books, search, and sorting.

    Returns:
        str: Rendered home page.
    """
    sort = request.args.get("sort", "title")
    search_term = request.args.get("search", "").strip()

    query = Book.query.join(Author)

    if search_term:
        query = query.filter(
            db.or_(
                Book.title.ilike(f"%{search_term}%"),
                Book.isbn.ilike(f"%{search_term}%"),
                Author.name.ilike(f"%{search_term}%")
            )
        )

    if sort == "author":
        books = query.order_by(Author.name.asc(), Book.title.asc()).all()
    elif sort == "rating":
        books = query.order_by(Book.rating.desc().nullslast(), Book.title.asc()).all()
    else:
        books = query.order_by(Book.title.asc()).all()

    return render_template(
        "home.html",
        books=books,
        selected_sort=sort,
        search_term=search_term
    )


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Show the add-author form and save a new author on POST.

    Returns:
        str: Rendered add-author page.
    """
    success_message = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birth_date_raw = request.form.get("birth_date", "").strip()
        date_of_death_raw = request.form.get("date_of_death", "").strip()

        if not name:
            flash("Bitte gib einen Autorennamen ein.")
            return redirect(url_for("add_author"))

        birth_date = parse_date(birth_date_raw)
        date_of_death = parse_date(date_of_death_raw)

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        success_message = f"Autor '{name}' wurde erfolgreich hinzugefügt."

    return render_template("add_author.html", success_message=success_message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Show the add-book form and save a new book on POST.

    Returns:
        str: Rendered add-book page.
    """
    success_message = None
    authors = Author.query.order_by(Author.name.asc()).all()

    if request.method == "POST":
        isbn = request.form.get("isbn", "").strip()
        title = request.form.get("title", "").strip()
        publication_year_raw = request.form.get("publication_year", "").strip()
        author_id_raw = request.form.get("author_id", "").strip()
        rating_raw = request.form.get("rating", "").strip()

        if not isbn or not title or not author_id_raw:
            flash("Bitte fülle ISBN, Titel und Autor aus.")
            return redirect(url_for("add_book"))

        publication_year = int(publication_year_raw) if publication_year_raw else None
        author_id = int(author_id_raw)
        rating = int(rating_raw) if rating_raw else None

        if rating is not None and not 1 <= rating <= 10:
            flash("Die Bewertung muss zwischen 1 und 10 liegen.")
            return redirect(url_for("add_book"))

        existing_book = Book.query.filter_by(isbn=isbn).first()
        if existing_book:
            flash("Ein Buch mit dieser ISBN existiert bereits.")
            return redirect(url_for("add_book"))

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id,
            rating=rating
        )
        db.session.add(new_book)
        db.session.commit()

        success_message = f"Buch '{title}' wurde erfolgreich hinzugefügt."

    return render_template(
        "add_book.html",
        authors=authors,
        success_message=success_message
    )


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    """
    Display details for a single book.

    Args:
        book_id (int): ID of the selected book.

    Returns:
        str: Rendered book detail page.
    """
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)


@app.route("/author/<int:author_id>")
def author_detail(author_id):
    """
    Display details for a single author.

    Args:
        author_id (int): ID of the selected author.

    Returns:
        str: Rendered author detail page.
    """
    author = Author.query.get_or_404(author_id)
    return render_template("author_detail.html", author=author)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Delete a book from the database.
    Delete the author too if no books remain.

    Args:
        book_id (int): ID of the book to delete.

    Returns:
        Response: Redirect to home page.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author
    book_title = book.title

    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author.id).count()
    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()

    flash(f"Buch '{book_title}' wurde erfolgreich gelöscht.")
    return redirect(url_for("home"))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    """
    Delete an author and all related books.

    Args:
        author_id (int): ID of the author to delete.

    Returns:
        Response: Redirect to home page.
    """
    author = Author.query.get_or_404(author_id)
    author_name = author.name

    db.session.delete(author)
    db.session.commit()

    flash(f"Autor '{author_name}' und alle zugehörigen Bücher wurden gelöscht.")
    return redirect(url_for("home"))


@app.route("/recommendation")
def recommendation():
    """
    Show the AI recommendation page.

    Returns:
        str: Rendered recommendation page.
    """
    books = Book.query.join(Author).order_by(Book.title.asc()).all()
    recommendation_text = generate_ai_recommendation(books)

    return render_template(
        "recommendation.html",
        recommendation_text=recommendation_text,
        books=books
    )


with app.app_context():
    os.makedirs(database_dir, exist_ok=True)
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)