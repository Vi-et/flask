"""
Contacts API endpoints
RESTful routes for contact management with Service Layer Pattern
"""
from flask import Blueprint, request
from models.contact import Contact
from config.database import db
from utils.response_helper import ResponseHelper
from utils.pagination_helper import PaginationHelper

# Create Blueprint với URL prefix
contacts_bp = Blueprint('contacts', __name__, url_prefix='/api/contacts')

@contacts_bp.route('/')
def get_contacts():
    """
    GET /api/contacts/
    Get all contacts with pagination
    """
    try:
        page, per_page = PaginationHelper.get_page_and_per_page()
        
        contacts = Contact.query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return ResponseHelper.success_response(
            data=[contact.to_dict() for contact in contacts.items],
            pagination=PaginationHelper.get_pagination_info(contacts)
        )
    except Exception as e:
        return ResponseHelper.error_response(str(e))

@contacts_bp.route('/<int:contact_id>')
def get_contact(contact_id):
    """
    GET /api/contacts/{id}
    Get single contact by ID
    """
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return ResponseHelper.not_found_response(f"Contact with ID {contact_id} not found")
        
        return ResponseHelper.success_response(
            data=contact.to_dict()
        )
    except Exception as e:
        return ResponseHelper.error_response(str(e))

@contacts_bp.route('/', methods=['POST'])
def create_contact():
    """
    POST /api/contacts/
    Create new contact
    """
    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.bad_request_response("No data provided")
        
        # Validate required fields
        required_fields = ['name', 'email']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return ResponseHelper.bad_request_response(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check if email already exists
        existing_contact = Contact.query.filter_by(email=data['email']).first()
        if existing_contact:
            return ResponseHelper.bad_request_response(f"Contact with email {data['email']} already exists")
        
        # Create contact
        contact = Contact(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            message=data.get('message')
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return ResponseHelper.created_response(
            data=contact.to_dict(),
            message="Contact created successfully"
        )
    except Exception as e:
        db.session.rollback()
        return ResponseHelper.error_response(str(e))

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """
    PUT /api/contacts/{id}
    Update contact by ID
    """
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return ResponseHelper.not_found_response(f"Contact with ID {contact_id} not found")
        
        data = request.get_json()
        if not data:
            return ResponseHelper.bad_request_response("No data provided")
        
        # Update fields if provided
        if 'name' in data:
            contact.name = data['name']
        if 'email' in data:
            # Check if new email already exists (exclude current contact)
            existing_contact = Contact.query.filter(
                Contact.email == data['email'], 
                Contact.id != contact_id
            ).first()
            if existing_contact:
                return ResponseHelper.bad_request_response(f"Contact with email {data['email']} already exists")
            contact.email = data['email']
        if 'phone' in data:
            contact.phone = data['phone']
        if 'message' in data:
            contact.message = data['message']
        
        db.session.commit()
        
        return ResponseHelper.success_response(
            data=contact.to_dict(),
            message="Contact updated successfully"
        )
    except Exception as e:
        db.session.rollback()
        return ResponseHelper.error_response(str(e))

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """
    DELETE /api/contacts/{id}
    Delete contact by ID
    """
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return ResponseHelper.not_found_response(f"Contact with ID {contact_id} not found")
        
        db.session.delete(contact)
        db.session.commit()
        
        return ResponseHelper.success_response(
            message="Contact deleted successfully"
        )
    except Exception as e:
        db.session.rollback()
        return ResponseHelper.error_response(str(e))