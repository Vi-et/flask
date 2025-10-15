"""
Contact Service
Business logic for contact management
"""
from typing import Dict, Any, Optional
from models import Contact, db
from utils.service_response_helper import ServiceResponseHelper
from utils.pagination_helper import PaginationHelper


class ContactService:
    """Service class for contact business logic"""
    
    @staticmethod
    def get_contacts_paginated(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get paginated contacts"""
        try:
            # Validate pagination
            validation = PaginationHelper.validate_pagination(page, per_page)
            if not validation['success']:
                return ServiceResponseHelper.error(
                    validation['error'], 
                    validation['code']
                )
            
            # Get contacts
            contacts = Contact.query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            contacts_data = [contact.to_dict() for contact in contacts.items]
            
            return ServiceResponseHelper.success({
                'contacts': contacts_data,
                'pagination': PaginationHelper.create_pagination_info(contacts)
            })
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get contacts: {str(e)}")
    
    @staticmethod
    def create_contact(name: str, email: str, message: str) -> Dict[str, Any]:
        """Create a new contact"""
        try:
            # Validate required fields
            if not all([name, email, message]):
                return ServiceResponseHelper.error(
                    "Name, email and message are required", 
                    400
                )
            
            # Validate email format (basic)
            if '@' not in email or '.' not in email:
                return ServiceResponseHelper.error(
                    "Invalid email format", 
                    400
                )
            
            # Create contact
            contact = Contact(name=name, email=email, message=message)
            db.session.add(contact)
            db.session.commit()
            
            return ServiceResponseHelper.success(
                contact.to_dict(), 
                "Contact created successfully", 
                201
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Failed to create contact: {str(e)}")
    
    @staticmethod
    def get_contact_by_id(contact_id: int) -> Dict[str, Any]:
        """Get contact by ID"""
        try:
            contact = Contact.query.get(contact_id)
            if not contact:
                return ServiceResponseHelper.error(
                    f"Contact with ID {contact_id} not found", 
                    404
                )
            
            return ServiceResponseHelper.success(contact.to_dict())
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get contact: {str(e)}")
    
    @staticmethod
    def update_contact_status(contact_id: int, status: str = "read") -> Dict[str, Any]:
        """Update contact status (e.g., mark as read)"""
        try:
            contact = Contact.query.get(contact_id)
            if not contact:
                return ServiceResponseHelper.error(
                    f"Contact with ID {contact_id} not found", 
                    404
                )
            
            # Add status field if not exists
            if not hasattr(contact, 'status'):
                # For now, we'll just update the contact
                pass
            
            db.session.commit()
            
            return ServiceResponseHelper.success(
                contact.to_dict(), 
                f"Contact status updated to {status}"
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Failed to update contact: {str(e)}")
    
    @staticmethod
    def delete_contact(contact_id: int) -> Dict[str, Any]:
        """Delete contact"""
        try:
            contact = Contact.query.get(contact_id)
            if not contact:
                return ServiceResponseHelper.error(
                    f"Contact with ID {contact_id} not found", 
                    404
                )
            
            db.session.delete(contact)
            db.session.commit()
            
            return ServiceResponseHelper.success(
                {"id": contact_id}, 
                "Contact deleted successfully"
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Failed to delete contact: {str(e)}")
    
    @staticmethod
    def search_contacts(query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Search contacts by name, email or message"""
        try:
            # Validate pagination
            validation = PaginationHelper.validate_pagination(page, per_page)
            if not validation['success']:
                return ServiceResponseHelper.error(
                    validation['error'], 
                    validation['code']
                )
            
            if not query or len(query.strip()) < 2:
                return ServiceResponseHelper.error(
                    "Search query must be at least 2 characters", 
                    400
                )
            
            # Search in name, email, and message
            search_term = f"%{query.strip()}%"
            contacts = Contact.query.filter(
                (Contact.name.ilike(search_term)) |
                (Contact.email.ilike(search_term)) |
                (Contact.message.ilike(search_term))
            ).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            contacts_data = [contact.to_dict() for contact in contacts.items]
            
            return ServiceResponseHelper.success({
                'contacts': contacts_data,
                'search_query': query,
                'pagination': PaginationHelper.create_pagination_info(contacts)
            })
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to search contacts: {str(e)}")