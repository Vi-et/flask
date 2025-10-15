"""
User Model
"""
from config.database import db
from models import BaseModel

class User(BaseModel):
    """Model cho bảng users"""
    __tablename__ = 'users'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Relationship với Post
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def to_dict(self):
        """Convert user to dictionary for JSON response"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'email': self.email,
            'posts_count': len(self.posts) if self.posts else 0
        })
        return base_dict
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_all_with_posts_count(cls):
        """Get all users with posts count"""
        return cls.query.outerjoin(cls.posts).group_by(cls.id).all()