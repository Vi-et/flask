"""
Contacts API endpoints
RESTful routes for contact management
"""
from flask import Blueprint, jsonify, request
from models.contact import Contact
from config.database import db

# Create Blueprint với URL prefix
contacts_bp = Blueprint('contacts', __name__, url_prefix='/api/contacts')

@contacts_bp.route('/')
def get_contacts():
    """
    GET /api/contacts/
    Get all contacts with pagination
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        contacts = Contact.query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': [contact.to_dict() for contact in contacts.items],
            'pagination': {
                'page': contacts.page,
                'pages': contacts.pages,
                'per_page': contacts.per_page,
                'total': contacts.total,
                'has_next': contacts.has_next,
                'has_prev': contacts.has_prev
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@contacts_bp.route('/<int:contact_id>')
def get_contact(contact_id):
    """
    GET /api/contacts/{id}
    Get single contact by ID
    """
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({
                'status': 'error',
                'message': 'Contact not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': contact.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@contacts_bp.route('/', methods=['POST'])
def create_contact():
    """
    POST /api/contacts/
    Create new contact message
    """
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'message']
        if not data or not all(k in data for k in required_fields):
            return jsonify({
                'status': 'error',
                'message': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        # Basic validation
        if not data['name'].strip() or not data['email'].strip() or not data['message'].strip():
            return jsonify({
                'status': 'error',
                'message': 'All fields must be non-empty'
            }), 400
        
        # Create contact
        new_contact = Contact(
            name=data['name'].strip(),
            email=data['email'].strip(),
            message=data['message'].strip()
        )
        
        if new_contact.save():
            return jsonify({
                'status': 'success',
                'data': new_contact.to_dict(),
                'message': 'Contact message created successfully'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create contact message'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """
    PUT /api/contacts/{id}
    Update contact (e.g., mark as read/replied)
    """
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({
                'status': 'error',
                'message': 'Contact not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Update fields (you can extend this based on your Contact model)
        if 'status' in data:
            contact.status = data['status']
        if 'notes' in data:
            contact.notes = data.get('notes', '')
        
        if contact.save():
            return jsonify({
                'status': 'success',
                'data': contact.to_dict(),
                'message': 'Contact updated successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update contact'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """
    DELETE /api/contacts/{id}
    Delete contact message
    """
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return jsonify({
                'status': 'error',
                'message': 'Contact not found'
            }), 404
        
        if contact.delete():
            return jsonify({
                'status': 'success',
                'message': 'Contact deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete contact'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500