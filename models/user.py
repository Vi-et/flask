"""
User Model with Authentication Support
"""
from config.database import db
from models import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta

class User(BaseModel):
    """Model cho bảng users"""
    __tablename__ = 'users'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship với Post
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for JSON response"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'posts_count': len(self.posts) if self.posts else 0
        })
        
        # Only include sensitive info if explicitly requested
        if include_sensitive:
            base_dict['password_hash'] = self.password_hash
            
        return base_dict
    
    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_tokens(self) -> dict:
        """Generate JWT access and refresh tokens"""
        additional_claims = {
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'user_id': self.id,
            'email': self.email
        }
        
        access_token = create_access_token(
            identity=self.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity=self.id,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour
        }
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_all_with_posts_count(cls):
        """Get all users with posts count"""
        return cls.query.outerjoin(cls.posts).group_by(cls.id).all()