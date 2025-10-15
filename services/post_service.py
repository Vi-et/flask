"""
Post Service
Business logic for post management
"""
from typing import Dict, Any, Optional
from models import Post, User, db
from utils.service_response_helper import ServiceResponseHelper
from utils.pagination_helper import PaginationHelper
from validators.post_validators import (
    validate_post_create,
    validate_post_update,
    validate_post_search,
    validate_post_bulk_operation
)


class PostService:
    """Service class for post business logic"""
    
    @staticmethod
    def get_posts_paginated(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get paginated posts with authors"""
        try:
            # Validate pagination
            validation = PaginationHelper.validate_pagination(page, per_page)
            if not validation['success']:
                return ServiceResponseHelper.error(
                    validation['error'], 
                    validation['code']
                )
            
            # Get posts with authors
            query = db.session.query(Post).join(User, Post.author_id == User.id)
            posts = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            # Format response
            posts_data = []
            for post in posts.items:
                post_dict = post.to_dict()
                post_dict['author_name'] = post.author.name if post.author else 'Unknown'
                posts_data.append(post_dict)
            
            return ServiceResponseHelper.success({
                'posts': posts_data,
                'pagination': PaginationHelper.create_pagination_info(posts)
            })
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get posts: {str(e)}")
    
    @staticmethod
    def create_post(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new post"""
        try:
            # Validate post creation data
            validation_result = validate_post_create(data)
            if not validation_result.is_valid:
                return ServiceResponseHelper.error(
                    validation_result.get_first_error(), 
                    400
                )
            
            title = data['title']
            content = data['content']
            author_id = data['author_id']
            
            # Create post
            post = Post(title=title, content=content, author_id=author_id)
            db.session.add(post)
            db.session.commit()
            
            # Get created post with author
            created_post = Post.query.get(post.id)
            post_data = created_post.to_dict()
            post_data['author_name'] = created_post.author.name
            
            return ServiceResponseHelper.success(
                post_data, 
                "Post created successfully", 
                201
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Failed to create post: {str(e)}")
    
    @staticmethod
    def get_post_by_id(post_id: int) -> Dict[str, Any]:
        """Get post by ID with author info"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return ServiceResponseHelper.error(
                    f"Post with ID {post_id} not found", 
                    404
                )
            
            post_data = post.to_dict()
            post_data['author_name'] = post.author.name if post.author else 'Unknown'
            
            return ServiceResponseHelper.success(post_data)
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get post: {str(e)}")
    
    @staticmethod
    def update_post(post_id: int, title: Optional[str] = None, 
                   content: Optional[str] = None) -> Dict[str, Any]:
        """Update post"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return ServiceResponseHelper.error(
                    f"Post with ID {post_id} not found", 
                    404
                )
            
            # Update fields
            if title:
                post.title = title
            if content:
                post.content = content
            
            db.session.commit()
            
            # Return updated post
            post_data = post.to_dict()
            post_data['author_name'] = post.author.name if post.author else 'Unknown'
            
            return ServiceResponseHelper.success(
                post_data, 
                "Post updated successfully"
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Failed to update post: {str(e)}")
    
    @staticmethod
    def delete_post(post_id: int) -> Dict[str, Any]:
        """Delete post"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return ServiceResponseHelper.error(
                    f"Post with ID {post_id} not found", 
                    404
                )
            
            db.session.delete(post)
            db.session.commit()
            
            return ServiceResponseHelper.success(
                {"id": post_id}, 
                "Post deleted successfully"
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Failed to delete post: {str(e)}")
    
    @staticmethod
    def get_posts_by_author(author_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get posts by author with pagination"""
        try:
            # Validate pagination
            validation = PaginationHelper.validate_pagination(page, per_page)
            if not validation['success']:
                return ServiceResponseHelper.error(
                    validation['error'], 
                    validation['code']
                )
            
            # Check if author exists
            author = User.query.get(author_id)
            if not author:
                return ServiceResponseHelper.error(
                    f"Author with ID {author_id} not found", 
                    404
                )
            
            # Get posts by author
            posts = Post.query.filter_by(author_id=author_id).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            posts_data = []
            for post in posts.items:
                post_dict = post.to_dict()
                post_dict['author_name'] = author.name
                posts_data.append(post_dict)
            
            return ServiceResponseHelper.success({
                'posts': posts_data,
                'author': author.to_dict(),
                'pagination': PaginationHelper.create_pagination_info(posts)
            })
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get posts by author: {str(e)}")