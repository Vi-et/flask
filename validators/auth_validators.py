import re

from flask import current_app

from models.user import User
from validators.validation_builder import BaseValidation, ValidationBuilder


class AuthValidationBuilder(ValidationBuilder):
    def require_email(self):
        def rule(data):
            email = data.get("email", "")
            if "@" not in email:
                self.errors.append("Please enter a valid email address")

        self.rules.append(rule)
        return self

    def require_password(self):
        def rule(data):
            password = data.get("password", "")
            min_length = current_app.config.get("SECURITY_PASSWORD_LENGTH_MIN", 8)
            if len(password) < min_length:
                self.errors.append(
                    f"Password must be at least {min_length} characters long"
                )

        self.rules.append(rule)
        return self

    def check_email_unique(self):
        def rule(data):
            email = data.get("email", "").strip().lower()
            user = User.query.filter_by(email=email).first()
            if user:
                self.errors.append("Email address is already registered")

        self.rules.append(rule)
        return self


class RegisterValidator(BaseValidation):
    _builder = (
        AuthValidationBuilder().require_email().require_password().check_email_unique()
    )
