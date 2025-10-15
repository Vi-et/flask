"""
Search API endpoints
Global search functionality across resources
"""
from flask import Blueprint, jsonify, request
from models.post import Post
from models.user import User
from models.contact import Contact

# Create Blueprint với URL prefix
search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/posts')
def search_posts():
    """
    GET /api/search/posts?q=query
    Search posts by title and content
    """
    try:
        query_string = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query_string:
            return jsonify({
                'status': 'success',
                'query': query_string,
                'results': [],
                'pagination': {
                    'page': 1,
                    'pages': 0,
                    'per_page': per_page,
                    'total': 0
                }
            })
        
        # Search posts
        posts = Post.search(query_string).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate relevance and prepare results
        results = []
        for post in posts.items:
            post_data = post.to_dict(include_author=True)
            post_data['relevance'] = post.calculate_relevance(query_string)
            results.append(post_data)
        
        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        return jsonify({
            'status': 'success',
            'query': query_string,
            'results': results,
            'pagination': {
                'page': posts.page,
                'pages': posts.pages,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@search_bp.route('/users')
def search_users():
    """
    GET /api/search/users?q=query
    Search users by name and email
    """
    try:
        query_string = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query_string:
            return jsonify({
                'status': 'success',
                'query': query_string,
                'results': [],
                'pagination': {
                    'page': 1,
                    'pages': 0,
                    'per_page': per_page,
                    'total': 0
                }
            })
        
        # Search users by name or email
        users = User.query.filter(
            User.name.contains(query_string) | 
            User.email.contains(query_string)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'status': 'success',
            'query': query_string,
            'results': [user.to_dict() for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@search_bp.route('/all')
def search_all():
    """
    GET /api/search/all?q=query
    Global search across all resources
    """
    try:
        query_string = request.args.get('q', '').strip()
        
        if not query_string:
            return jsonify({
                'status': 'success',
                'query': query_string,
                'results': {
                    'posts': [],
                    'users': [],
                    'contacts': []
                },
                'total_count': 0
            })
        
        # Search across all resources
        posts = Post.search(query_string).limit(5).all()
        users = User.query.filter(
            User.name.contains(query_string) | 
            User.email.contains(query_string)
        ).limit(5).all()
        contacts = Contact.query.filter(
            Contact.name.contains(query_string) |
            Contact.email.contains(query_string) |
            Contact.message.contains(query_string)
        ).limit(5).all()
        
        # Prepare results
        results = {
            'posts': [post.to_dict(include_author=True) for post in posts],
            'users': [user.to_dict() for user in users],
            'contacts': [contact.to_dict() for contact in contacts]
        }
        
        total_count = len(results['posts']) + len(results['users']) + len(results['contacts'])
        
        return jsonify({
            'status': 'success',
            'query': query_string,
            'results': results,
            'total_count': total_count
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@search_bp.route('/')
def search_general():
    """
    GET /api/search/?q=query&type=posts|users|all
    General search endpoint with type parameter
    """
    try:
        query_string = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all').lower()
        
        if search_type == 'posts':
            return search_posts()
        elif search_type == 'users':
            return search_users()
        elif search_type == 'all':
            return search_all()
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid search type. Use: posts, users, or all'
            }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500