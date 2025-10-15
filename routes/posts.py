"""
Posts API endpoints
RESTful routes for post management with Service Layer Pattern
"""
from flask import Blueprint, request
from models.post import Post
from models.user import User
from config.database import db
from utils.response_helper import ResponseHelper
from utils.pagination_helper import PaginationHelper

# Create Blueprint với URL prefix
posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')

@posts_bp.route('/')
def get_posts():
    """
    GET /api/posts/
    Get all posts with pagination and filtering
    """
    try:
        page, per_page = PaginationHelper.get_page_and_per_page()
        author_id = request.args.get('author_id', type=int)
        
        # Base query
        query = Post.query
        
        # Filter by author if specified
        if author_id:
            query = query.filter_by(author_id=author_id)
        
        # Pagination
        posts = query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return ResponseHelper.success_response(
            data=[post.to_dict(include_author=True) for post in posts.items],
            pagination=PaginationHelper.get_pagination_info(posts)
        )
    except Exception as e:
        return ResponseHelper.error_response(str(e))

@posts_bp.route('/<int:post_id>')
def get_post(post_id):
    """
    GET /api/posts/{id}
    Get single post by ID
    """
    try:
        post = Post.query.get(post_id)
        if not post:
            return ResponseHelper.not_found_response(f"Post with ID {post_id} not found")
        
        return ResponseHelper.success_response(
            data=post.to_dict(include_author=True)
        )
    except Exception as e:
        return ResponseHelper.error_response(str(e))

@posts_bp.route('/', methods=['POST'])
def create_post():
    """
    POST /api/posts/
    Create new post
    """
    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.bad_request_response("No data provided")
        
        # Validate required fields
        if 'title' not in data or 'content' not in data or 'author_id' not in data:
            return ResponseHelper.bad_request_response("Missing required fields: title, content, author_id")
        
        # Check if author exists
        author = User.query.get(data['author_id'])
        if not author:
            return ResponseHelper.not_found_response(f"User with ID {data['author_id']} not found")
        
        # Create post
        post = Post(
            title=data['title'],
            content=data['content'],
            author_id=data['author_id']
        )
        
        db.session.add(post)
        db.session.commit()
        
        return ResponseHelper.created_response(
            data=post.to_dict(include_author=True),
            message="Post created successfully"
        )
    except Exception as e:
        db.session.rollback()
        return ResponseHelper.error_response(str(e))

@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    PUT /api/posts/{id}
    Update post by ID
    """
    try:
        post = Post.query.get(post_id)
        if not post:
            return ResponseHelper.not_found_response(f"Post with ID {post_id} not found")
        
        data = request.get_json()
        if not data:
            return ResponseHelper.bad_request_response("No data provided")
        
        # Update fields if provided
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        
        db.session.commit()
        
        return ResponseHelper.success_response(
            data=post.to_dict(include_author=True),
            message="Post updated successfully"
        )
    except Exception as e:
        db.session.rollback()
        return ResponseHelper.error_response(str(e))

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    DELETE /api/posts/{id}
    Delete post by ID
    """
    try:
        post = Post.query.get(post_id)
        if not post:
            return ResponseHelper.not_found_response(f"Post with ID {post_id} not found")
        
        db.session.delete(post)
        db.session.commit()
        
        return ResponseHelper.success_response(
            message="Post deleted successfully"
        )
    except Exception as e:
        db.session.rollback()
        return ResponseHelper.error_response(str(e))