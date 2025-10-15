"""
Post Validators
Validation logic for post management operations
"""
from typing import Dict, Any
from validators import BaseValidator, ValidationResult
from models.user import User


class PostCreateValidator(BaseValidator):
    """Validator for creating posts"""
    
    def validate(self) -> ValidationResult:
        """Validate post creation data"""
        
        # Check required fields
        required_fields = ['title', 'content', 'author_id']
        self.validate_required_fields(required_fields)
        
        # If required fields are missing, return early
        if not self.result.is_valid:
            return self.result
        
        # Validate individual fields
        self.validate_title()
        self.validate_content()
        self.validate_author_id()
        
        # Validate optional fields
        if 'status' in self.data:
            allowed_statuses = ['draft', 'published', 'archived']
            self.validate_choice('status', allowed_statuses)
        
        if 'tags' in self.data:
            self.validate_tags()
        
        return self.result
    
    def validate_title(self) -> bool:
        """Validate post title"""
        return self.validate_string_length('title', min_length=3, max_length=200)
    
    def validate_content(self) -> bool:
        """Validate post content"""
        return self.validate_string_length('content', min_length=10, max_length=10000)
    
    def validate_author_id(self) -> bool:
        """Validate author ID and check if author exists"""
        # Validate it's a positive integer
        if not self.validate_integer('author_id', min_value=1):
            return False
        
        # Check if author exists
        author_id = self.data['author_id']
        author = User.query.get(author_id)
        
        if not author:
            self.result.add_field_error('author_id', f'Author with ID {author_id} not found')
            return False
        
        if not author.is_active:
            self.result.add_field_error('author_id', 'Author account is not active')
            return False
        
        return True
    
    def validate_tags(self) -> bool:
        """Validate post tags"""
        tags = self.data.get('tags', [])
        
        if not isinstance(tags, list):
            self.result.add_field_error('tags', 'Tags must be a list')
            return False
        
        if len(tags) > 10:
            self.result.add_field_error('tags', 'Cannot have more than 10 tags')
            return False
        
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                self.result.add_field_error('tags', f'Tag at position {i + 1} must be a string')
                return False
            
            tag_clean = tag.strip()
            if len(tag_clean) < 2:
                self.result.add_field_error('tags', f'Tag at position {i + 1} must be at least 2 characters')
                return False
            
            if len(tag_clean) > 30:
                self.result.add_field_error('tags', f'Tag at position {i + 1} must not exceed 30 characters')
                return False
        
        return True


class PostUpdateValidator(BaseValidator):
    """Validator for updating posts"""
    
    def validate(self) -> ValidationResult:
        """Validate post update data"""
        
        # At least one field must be provided
        updatable_fields = ['title', 'content', 'status', 'tags']
        has_update_field = any(field in self.data for field in updatable_fields)
        
        if not has_update_field:
            self.result.add_error('At least one field must be provided for update')
            return self.result
        
        # Validate individual fields if present
        if 'title' in self.data:
            self.validate_title()
        
        if 'content' in self.data:
            self.validate_content()
        
        if 'status' in self.data:
            allowed_statuses = ['draft', 'published', 'archived']
            self.validate_choice('status', allowed_statuses)
        
        if 'tags' in self.data:
            self.validate_tags()
        
        return self.result
    
    def validate_title(self) -> bool:
        """Validate title update"""
        if not str(self.data.get('title', '')).strip():
            self.result.add_field_error('title', 'Title cannot be empty')
            return False
        
        return self.validate_string_length('title', min_length=3, max_length=200)
    
    def validate_content(self) -> bool:
        """Validate content update"""
        if not str(self.data.get('content', '')).strip():
            self.result.add_field_error('content', 'Content cannot be empty')
            return False
        
        return self.validate_string_length('content', min_length=10, max_length=10000)
    
    def validate_tags(self) -> bool:
        """Validate post tags"""
        tags = self.data.get('tags', [])
        
        if not isinstance(tags, list):
            self.result.add_field_error('tags', 'Tags must be a list')
            return False
        
        if len(tags) > 10:
            self.result.add_field_error('tags', 'Cannot have more than 10 tags')
            return False
        
        for i, tag in enumerate(tags):
            if not isinstance(tag, str):
                self.result.add_field_error('tags', f'Tag at position {i + 1} must be a string')
                return False
            
            tag_clean = tag.strip()
            if len(tag_clean) < 2:
                self.result.add_field_error('tags', f'Tag at position {i + 1} must be at least 2 characters')
                return False
            
            if len(tag_clean) > 30:
                self.result.add_field_error('tags', f'Tag at position {i + 1} must not exceed 30 characters')
                return False
        
        return True


class PostSearchValidator(BaseValidator):
    """Validator for post search parameters"""
    
    def validate(self) -> ValidationResult:
        """Validate search parameters"""
        
        # Validate query if provided
        if 'query' in self.data:
            query = str(self.data.get('query', '')).strip()
            if len(query) < 2:
                self.result.add_field_error('query', 'Search query must be at least 2 characters')
        
        # Validate pagination parameters
        if 'page' in self.data:
            self.validate_integer('page', min_value=1)
        
        if 'per_page' in self.data:
            self.validate_integer('per_page', min_value=1, max_value=100)
        
        # Validate filter parameters
        if 'status' in self.data:
            allowed_statuses = ['draft', 'published', 'archived', 'all']
            self.validate_choice('status', allowed_statuses)
        
        if 'author_id' in self.data:
            self.validate_integer('author_id', min_value=1)
        
        if 'tag' in self.data:
            tag = str(self.data.get('tag', '')).strip()
            if len(tag) < 2:
                self.result.add_field_error('tag', 'Tag filter must be at least 2 characters')
        
        # Validate sorting parameters
        if 'sort_by' in self.data:
            allowed_sort_fields = ['created_at', 'updated_at', 'title', 'author']
            self.validate_choice('sort_by', allowed_sort_fields)
        
        if 'sort_order' in self.data:
            allowed_orders = ['asc', 'desc']
            self.validate_choice('sort_order', allowed_orders)
        
        return self.result


class PostBulkOperationValidator(BaseValidator):
    """Validator for bulk operations on posts"""
    
    def validate(self) -> ValidationResult:
        """Validate bulk operation data"""
        
        # Check required fields
        required_fields = ['post_ids', 'operation']
        self.validate_required_fields(required_fields)
        
        if not self.result.is_valid:
            return self.result
        
        # Validate post_ids
        self.validate_post_ids()
        
        # Validate operation
        allowed_operations = ['publish', 'draft', 'archive', 'delete']
        self.validate_choice('operation', allowed_operations)
        
        return self.result
    
    def validate_post_ids(self) -> bool:
        """Validate post IDs list"""
        post_ids = self.data.get('post_ids', [])
        
        if not isinstance(post_ids, list):
            self.result.add_field_error('post_ids', 'Must be a list of post IDs')
            return False
        
        if not post_ids:
            self.result.add_field_error('post_ids', 'At least one post ID must be provided')
            return False
        
        if len(post_ids) > 50:  # Limit bulk operations
            self.result.add_field_error('post_ids', 'Cannot process more than 50 posts at once')
            return False
        
        # Validate each ID is a positive integer
        for i, post_id in enumerate(post_ids):
            try:
                id_val = int(post_id)
                if id_val <= 0:
                    self.result.add_field_error('post_ids', f'Invalid post ID at position {i + 1}')
                    return False
            except (ValueError, TypeError):
                self.result.add_field_error('post_ids', f'Invalid post ID at position {i + 1}')
                return False
        
        return True


# Validator factory functions
def validate_post_create(data: Dict[str, Any]) -> ValidationResult:
    """Validate post creation data"""
    validator = PostCreateValidator(data)
    return validator.validate()


def validate_post_update(data: Dict[str, Any]) -> ValidationResult:
    """Validate post update data"""
    validator = PostUpdateValidator(data)
    return validator.validate()


def validate_post_search(data: Dict[str, Any]) -> ValidationResult:
    """Validate post search parameters"""
    validator = PostSearchValidator(data)
    return validator.validate()


def validate_post_bulk_operation(data: Dict[str, Any]) -> ValidationResult:
    """Validate bulk operation data"""
    validator = PostBulkOperationValidator(data)
    return validator.validate()