"""
Protected routes for testing JWT authentication
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

protected_bp = Blueprint("protected", __name__, url_prefix="/api")


@protected_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information from JWT token"""
    current_user_id = get_jwt_identity()
    jwt_claims = get_jwt()

    return jsonify(
        {
            "success": True,
            "data": {
                "user_id": current_user_id,
                "email": jwt_claims.get("email"),
                "is_admin": jwt_claims.get("is_admin"),
                "is_active": jwt_claims.get("is_active"),
                "fs_uniquifier": jwt_claims.get("fs_uniquifier"),
            },
        }
    )


@protected_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """Get full user profile from database"""
    from models.user import User

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({"success": True, "data": {"user": user.to_dict()}})
