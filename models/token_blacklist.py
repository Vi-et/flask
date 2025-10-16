"""
Token Blacklist Model
For managing revoked JWT tokens
"""
from datetime import datetime
from typing import Optional

from config.database import db
from models import BaseModel


class TokenBlacklist(BaseModel):
    """Model for blacklisted JWT tokens"""

    __tablename__ = "token_blacklist"

    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)  # 'access' or 'refresh'
    blacklisted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(100), nullable=True)

    # Relationship
    user = db.relationship("User", backref="blacklisted_tokens")

    def __repr__(self):
        return f"<TokenBlacklist {self.jti[:8]}... - {self.token_type}>"

    def to_dict(self):
        """Convert to dictionary for JSON response"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "jti": self.jti,
                "user_id": self.user_id,
                "token_type": self.token_type,
                "blacklisted_at": self.blacklisted_at.isoformat(),
                "expires_at": self.expires_at.isoformat(),
                "reason": self.reason,
            }
        )
        return base_dict

    @classmethod
    def is_token_revoked(cls, jti: str) -> bool:
        """Check if a token JTI is blacklisted"""
        return cls.query.filter_by(jti=jti).first() is not None

    @classmethod
    def revoke_token(
        cls, jti: str, user_id: int, token_type: str, reason: Optional[str] = None
    ) -> "TokenBlacklist":
        """Add token to blacklist"""
        blacklisted_token = cls(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            reason=reason or "manual_revoke",
            expires_at=datetime.utcnow(),  # Will be updated with actual expiry
        )
        blacklisted_token.save()
        return blacklisted_token

    @classmethod
    def revoke_all_user_tokens(cls, user_id: int, reason: str = "logout_all") -> None:
        """Revoke all active tokens for a user"""
        # This would require getting all active tokens for user
        # Implementation depends on how you track active sessions
        pass

    @classmethod
    def cleanup_expired_tokens(cls):
        """Remove expired blacklisted tokens (cleanup job)"""
        expired_tokens = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for token in expired_tokens:
            token.delete()
        return len(expired_tokens)
