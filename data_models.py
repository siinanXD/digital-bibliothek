from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Represent an author in the digital library.
    """

    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship(
        "Book",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """
        Return a developer-friendly representation of the author.

        Returns:
            str: Debug representation.
        """
        return f"<Author {self.name}>"

    def __str__(self):
        """
        Return a user-friendly representation of the author.

        Returns:
            str: Author name.
        """
        return self.name


class Book(db.Model):
    """
    Represent a book in the digital library.
    """

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    author = db.relationship("Author", back_populates="books")

    def __repr__(self):
        """
        Return a developer-friendly representation of the book.

        Returns:
            str: Debug representation.
        """
        return f"<Book {self.title}>"

    def __str__(self):
        """
        Return a user-friendly representation of the book.

        Returns:
            str: Book title.
        """
        return self.title