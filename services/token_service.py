"""
Token Management Service
Business logic for JWT token blacklist and session management
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from flask_jwt_extended import get_jwt, get_jwt_identity

from constants.token_constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from models.token_blacklist import TokenBlacklist
from utils.service_response_helper import ServiceResponseHelper


class TokenService:
    """Service class for token management and blacklist operations"""

    @staticmethod
    def revoke_token(
        jti: str, user_id: int, token_type: str, reason: str = "manual_revoke"
    ) -> Dict[str, Any]:
        """
        Add token to blacklist

        Args:
            jti: JWT ID to blacklist
            user_id: User ID who owns the token
            token_type: 'access' or 'refresh'
            reason: Reason for revocation

        Returns:
            Service response dictionary
        """
        try:
            # Check if already blacklisted
            if TokenBlacklist.is_token_revoked(jti):
                return ServiceResponseHelper.bad_request("Token already revoked")

            # Calculate expiry based on token type
            if token_type == ACCESS_TOKEN_TYPE:
                expires_at = datetime.utcnow() + timedelta(hours=1)
            else:  # refresh
                expires_at = datetime.utcnow() + timedelta(days=30)

            # Create blacklist entry
            blacklisted_token = TokenBlacklist(
                jti=jti,
                user_id=user_id,
                token_type=token_type,
                reason=reason,
                expires_at=expires_at,
            )

            if blacklisted_token.save():
                return ServiceResponseHelper.success(
                    blacklisted_token.to_dict(),
                    f"{token_type.title()} token revoked successfully",
                )
            else:
                return ServiceResponseHelper.operation_failed("revoke token")

        except Exception as e:
            return ServiceResponseHelper.error(f"Token revocation failed: {str(e)}")

    @staticmethod
    def revoke_current_token(reason: str = "logout") -> Dict[str, Any]:
        """
        Revoke currently used token

        Args:
            reason: Reason for revocation

        Returns:
            Service response dictionary
        """
        try:
            # Get current token info
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            jti = claims.get("jti")

            if not jti:
                return ServiceResponseHelper.bad_request("Token JTI not found")

            # Determine token type based on claims
            token_type = "refresh" if claims.get("type") == "refresh" else "access"

            return TokenService.revoke_token(jti, current_user_id, token_type, reason)

        except Exception as e:
            return ServiceResponseHelper.error(
                f"Current token revocation failed: {str(e)}"
            )

    @staticmethod
    def revoke_all_user_tokens(
        user_id: int, reason: str = "logout_all_sessions"
    ) -> Dict[str, Any]:
        """
        Revoke all active tokens for a user (logout from all devices)

        Args:
            user_id: User ID
            reason: Reason for mass revocation

        Returns:
            Service response dictionary
        """
        try:
            # For now, we can't revoke all active tokens since we don't track them
            # This would require storing active sessions or JTIs
            # We can only revoke the current token

            return ServiceResponseHelper.success(
                {"revoked_count": 0}, "Mass token revocation not yet implemented"
            )

        except Exception as e:
            return ServiceResponseHelper.error(
                f"Mass token revocation failed: {str(e)}"
            )

    @staticmethod
    def is_token_valid(jti: str) -> bool:
        """
        Check if token is valid (not blacklisted)

        Args:
            jti: JWT ID to check

        Returns:
            True if valid, False if blacklisted
        """
        return not TokenBlacklist.is_token_revoked(jti)

    @staticmethod
    def is_token_revoked(jti: str) -> bool:
        """
        Check if token is revoked (blacklisted)

        Args:
            jti: JWT ID to check

        Returns:
            True if revoked, False if still valid
        """
        return TokenBlacklist.is_token_revoked(jti)

    @staticmethod
    def get_user_blacklisted_tokens(user_id: int) -> Dict[str, Any]:
        """
        Get all blacklisted tokens for a user

        Args:
            user_id: User ID

        Returns:
            Service response with blacklisted tokens
        """
        try:
            blacklisted_tokens = (
                TokenBlacklist.query.filter_by(user_id=user_id)
                .order_by(TokenBlacklist.blacklisted_at.desc())
                .all()
            )

            tokens_data = [token.to_dict() for token in blacklisted_tokens]

            return ServiceResponseHelper.success(
                tokens_data, f"Retrieved {len(tokens_data)} blacklisted tokens"
            )

        except Exception as e:
            return ServiceResponseHelper.error(
                f"Failed to retrieve blacklisted tokens: {str(e)}"
            )

    @staticmethod
    def cleanup_expired_tokens() -> Dict[str, Any]:
        """
        Remove expired blacklisted tokens (cleanup job)

        Returns:
            Service response with cleanup results
        """
        try:
            cleaned_count = TokenBlacklist.cleanup_expired_tokens()

            return ServiceResponseHelper.success(
                {"cleaned_count": cleaned_count},
                f"Cleaned up {cleaned_count} expired tokens",
            )

        except Exception as e:
            return ServiceResponseHelper.error(f"Token cleanup failed: {str(e)}")

    @staticmethod
    def get_token_info() -> Dict[str, Any]:
        """
        Get information about current token

        Returns:
            Service response with token information
        """
        try:
            claims = get_jwt()
            user_id = get_jwt_identity()

            token_info = {
                "user_id": user_id,
                "jti": claims.get("jti"),
                "type": claims.get("type", "access"),
                "exp": claims.get("exp"),
                "iat": claims.get("iat"),
                "is_admin": claims.get("is_admin"),
                "is_active": claims.get("is_active"),
                "email": claims.get("email"),
            }

            # Check if blacklisted
            jti = claims.get("jti")
            if jti:
                token_info["is_blacklisted"] = TokenBlacklist.is_token_revoked(jti)

            return ServiceResponseHelper.success(
                token_info, "Token information retrieved successfully"
            )

        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get token info: {str(e)}")
