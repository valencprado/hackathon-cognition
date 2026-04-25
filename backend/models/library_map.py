"""Library map and book-location models."""

from database import db


class LibraryMap(db.Model):
    __tablename__ = "library_maps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant = db.Column(db.String(100), nullable=False, unique=True, index=True)
    image_url = db.Column(db.String(500), nullable=False)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "tenant": self.tenant,
            "image_url": self.image_url,
            "width": self.width,
            "height": self.height,
        }


class BookLocation(db.Model):
    __tablename__ = "book_locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(
        db.Integer, db.ForeignKey("books.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    label = db.Column(db.String(100), nullable=True)
    shelf = db.Column(db.String(100), nullable=True)
    section = db.Column(db.String(100), nullable=True)
    aisle = db.Column(db.String(50), nullable=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    floor = db.Column(db.String(50), nullable=True)

    book = db.relationship("Book", back_populates="location")

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "label": self.label,
            "shelf": self.shelf,
            "section": self.section,
            "aisle": self.aisle,
            "x": self.x,
            "y": self.y,
            "floor": self.floor,
        }
