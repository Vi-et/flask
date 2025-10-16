"""
Role Model for Flask-Security-Too
"""
from flask_security import RoleMixin

from config.database import db
from models import BaseModel


class Role(BaseModel, RoleMixin):
    """Model for user roles"""

    __tablename__ = "roles"

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Role {self.name}>"

    def to_dict(self):
        """Convert role to dictionary"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "name": self.name,
                "description": self.description,
            }
        )
        return base_dict


# Association table for many-to-many relationship between users and roles
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)
