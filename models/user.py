"""
User Model with Authentication Support
"""
import uuid
from datetime import datetime, timedelta
from typing import cast

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from config.database import db
from models import BaseModel


class User(BaseModel):
    """Model cho bảng users"""

    __tablename__ = "users"

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(
        db.String(255), nullable=False
    )  # Flask-Security uses 'password' not 'password_hash'
    active = db.Column(
        db.Boolean, default=True, nullable=False
    )  # Flask-Security uses 'active' not 'is_active'
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_login_at = db.Column(
        db.DateTime, nullable=True
    )  # Flask-Security uses 'last_login_at'

    # Flask-Security required fields (4.0+)
    fs_uniquifier = db.Column(
        db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    # Relationship với Post (lazy loading to avoid circular import issues)
    posts = db.relationship(
        "Post",
        backref=db.backref("author", lazy="select"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.name}>"

    def to_dict(self, include_password: bool = False) -> dict:
        """Convert user to dictionary for API responses."""
        base_dict = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login_at.isoformat()
            if self.last_login_at
            else None,
        }

        if include_password:
            base_dict["password_hash"] = self.password

        return base_dict

    def set_password(self, password: str) -> None:
        """Hash and set password."""
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return check_password_hash(self.password, password)  # type: ignore[no-any-return]

    def generate_tokens(self) -> dict:
        """Generate JWT access and refresh tokens with JTI for blacklist support"""
        import uuid

        # Generate unique JTI (JWT ID) for each token
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())

        additional_claims = {
            "is_admin": self.is_admin,
            "is_active": self.active,
            "user_id": self.id,
            "email": self.email,
        }

        access_token = create_access_token(
            identity=self.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1),
            additional_headers={"jti": access_jti},
        )

        refresh_token = create_refresh_token(
            identity=self.id,
            expires_delta=timedelta(days=30),
            additional_headers={"jti": refresh_jti},
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour
            "access_jti": access_jti,  # For blacklist management
            "refresh_jti": refresh_jti,  # For blacklist management
        }

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.now()
        db.session.commit()

    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
