"""
Contact Model
"""
from config.database import db
from models import BaseModel

class Contact(BaseModel):
    """Model cho contact messages"""
    __tablename__ = 'contacts'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Contact from {self.name}>'
    
    def to_dict(self):
        """Convert contact to dictionary for JSON response"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'is_read': self.is_read
        })
        return base_dict
    
    def mark_as_read(self):
        """Mark contact as read"""
        self.is_read = True
        return self.save()
    
    @classmethod
    def get_unread(cls):
        """Get all unread contacts"""
        return cls.query.filter_by(is_read=False).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent(cls, limit=10):
        """Get recent contacts"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()