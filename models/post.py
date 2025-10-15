"""
Post Model
"""
from config.database import db
from models import BaseModel


class Post(BaseModel):
    """Model cho bảng posts"""

    __tablename__ = "posts"

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Foreign key
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"

    def to_dict(self, include_author=False):
        """Convert post to dictionary for JSON response"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "title": self.title,
                "content": self.content,
                "author_id": self.author_id,
                "word_count": len(self.content.split()) if self.content else 0,
                "content_length": len(self.content) if self.content else 0,
            }
        )

        if include_author and self.author:
            base_dict["author"] = {
                "id": self.author.id,
                "name": self.author.name,
                "email": self.author.email,
            }

        return base_dict

    @classmethod
    def get_by_author(cls, author_id):
        """Get posts by author ID"""
        return cls.query.filter_by(author_id=author_id).all()

    @classmethod
    def search(cls, query_string):
        """Search posts by title and content"""
        search_term = f"%{query_string}%"
        return cls.query.filter(
            db.or_(cls.title.ilike(search_term), cls.content.ilike(search_term))
        ).order_by(cls.created_at.desc())

    @classmethod
    def get_recent(cls, limit=5):
        """Get recent posts"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    def calculate_relevance(self, query_string):
        """Calculate relevance score for search"""
        title_matches = self.title.lower().count(query_string.lower()) * 3
        content_matches = self.content.lower().count(query_string.lower())
        return title_matches + content_matches
