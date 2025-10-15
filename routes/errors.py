"""
Error handlers - API Only
"""
from flask import Blueprint, jsonify, request

# Create Blueprint
errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors - API only"""
    return jsonify({
        'status': 'error',
        'message': 'Resource not found',
        'error_code': 404,
        'path': request.path
    }), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors - API only"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error_code': 500,
        'path': request.path
    }), 500

@errors_bp.app_errorhandler(400)
def bad_request_error(error):
    """Handle 400 errors - API only"""
    return jsonify({
        'status': 'error',
        'message': 'Bad request',
        'error_code': 400,
        'path': request.path
    }), 400

@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors - API only"""
    return jsonify({
        'status': 'error',
        'message': 'Forbidden',
        'error_code': 403,
        'path': request.path
    }), 403