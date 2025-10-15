"""
Posts API endpoints
RESTful routes for post management
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
            return jsonify({
                'status': 'error',
                'message': 'Post not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': post.to_dict(include_author=True)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@posts_bp.route('/', methods=['POST'])
def create_post():
    """
    POST /api/posts/
    Create new post
    """
    try:
        data = request.get_json()
        
        required_fields = ['title', 'content', 'author_id']
        if not data or not all(k in data for k in required_fields):
            return jsonify({
                'status': 'error',
                'message': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        # Check if author exists
        author = User.query.get(data['author_id'])
        if not author:
            return jsonify({
                'status': 'error',
                'message': 'Author not found'
            }), 404
        
        # Create post
        new_post = Post(
            title=data['title'],
            content=data['content'],
            author_id=data['author_id']
        )
        
        if new_post.save():
            return jsonify({
                'status': 'success',
                'data': new_post.to_dict(include_author=True),
                'message': 'Post created successfully'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create post'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    PUT /api/posts/{id}
    Update post
    """
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({
                'status': 'error',
                'message': 'Post not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Update fields
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        
        if post.save():
            return jsonify({
                'status': 'success',
                'data': post.to_dict(include_author=True),
                'message': 'Post updated successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update post'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    DELETE /api/posts/{id}
    Delete post
    """
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({
                'status': 'error',
                'message': 'Post not found'
            }), 404
        
        if post.delete():
            return jsonify({
                'status': 'success',
                'message': 'Post deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete post'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500