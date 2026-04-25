"""CRUD endpoints for books."""

from flask import Blueprint, jsonify, request

from database import db
from models.book import Book
from models.library_map import BookLocation

books_bp = Blueprint("books", __name__, url_prefix="/admin/books")


@books_bp.route("", methods=["GET"])
def list_books():
    """List all books for a tenant.

    Query params:
        tenant (str): required
        format_type (str): optional filter (book | comic | journal)
    """
    tenant = request.args.get("tenant", "").strip()
    if not tenant:
        return jsonify({"error": "tenant query parameter is required"}), 400

    query = Book.query.filter_by(tenant=tenant)

    format_type = request.args.get("format_type", "").strip()
    if format_type:
        query = query.filter_by(format_type=format_type)

    books = query.order_by(Book.title).all()
    return jsonify([b.to_dict() for b in books]), 200


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200


@books_bp.route("", methods=["POST"])
def create_book():
    """Create a new book.

    JSON body:
        tenant, title, author (required)
        year, isbn, format_type, synopsis (optional)
        location: { x, y, label?, floor? } (optional)
    """
    data = request.get_json(silent=True) or {}
    errors = _validate_book(data)
    if errors:
        return jsonify({"errors": errors}), 400

    book = Book(
        tenant=data["tenant"],
        title=data["title"],
        author=data["author"],
        year=data.get("year"),
        isbn=data.get("isbn"),
        format_type=data.get("format_type", "book"),
        synopsis=data.get("synopsis"),
    )
    db.session.add(book)
    db.session.flush()

    loc = data.get("location")
    if loc and "x" in loc and "y" in loc:
        book_loc = BookLocation(
            book_id=book.id,
            x=loc["x"],
            y=loc["y"],
            label=loc.get("label"),
            floor=loc.get("floor"),
        )
        db.session.add(book_loc)

    db.session.commit()
    return jsonify(book.to_dict()), 201


@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id: int):
    """Update an existing book."""
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json(silent=True) or {}

    for field in ("title", "author", "year", "isbn", "format_type", "synopsis"):
        if field in data:
            setattr(book, field, data[field])

    loc = data.get("location")
    if loc is not None:
        if book.location:
            for attr in ("x", "y", "label", "floor"):
                if attr in loc:
                    setattr(book.location, attr, loc[attr])
        elif "x" in loc and "y" in loc:
            book_loc = BookLocation(
                book_id=book.id,
                x=loc["x"],
                y=loc["y"],
                label=loc.get("label"),
                floor=loc.get("floor"),
            )
            db.session.add(book_loc)

    db.session.commit()
    return jsonify(book.to_dict()), 200


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id: int):
    """Delete a book and its location."""
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200


def _validate_book(data: dict) -> list[str]:
    errors = []
    if not data.get("tenant", "").strip():
        errors.append("tenant is required")
    if not data.get("title", "").strip():
        errors.append("title is required")
    if not data.get("author", "").strip():
        errors.append("author is required")

    fmt = data.get("format_type", "book")
    if fmt not in ("book", "comic", "journal"):
        errors.append("format_type must be one of: book, comic, journal")

    return errors
