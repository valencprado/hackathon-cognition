"""Book model."""

from database import db


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(300), nullable=False)
    author = db.Column(db.String(300), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    format_type = db.Column(
        db.String(20), nullable=False, default="book"
    )  # book | comic | journal
    synopsis = db.Column(db.Text, nullable=True)

    location = db.relationship(
        "BookLocation", back_populates="book", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self):
        data = {
            "id": self.id,
            "tenant": self.tenant,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "isbn": self.isbn,
            "format_type": self.format_type,
            "synopsis": self.synopsis,
        }
        if self.location:
            data["location"] = self.location.to_dict()
        return data
