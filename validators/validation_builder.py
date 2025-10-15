class ValidationBuilder:
    def __init__(self):
        self.rules = []
        self.errors = []

    def push_error(self, message):
        """Push error message to errors list"""
        self.errors.append(message)

    def build(self):
        """Build the validation function"""
        def validator(**kwargs):
            # Reset errors for each validation
            self.errors = []
            
            # Pass self to rules so they can push errors
            for rule in self.rules:
                rule(self, **kwargs)
                
            return {
                'is_valid': len(self.errors) == 0,
                'errors': self.errors.copy(),
                'first_error': self.errors[0] if self.errors else None
            }

        # Store reference for is_valid method
        self._validator = validator
        return validator


class BaseValidation:
    @classmethod
    def get_builder(cls):
        """Override this to return the validation builder"""
        return ValidationBuilder()

    @classmethod
    def validate(cls, **kwargs):
        """Validate data and return result"""
        builder = cls.get_builder()
        validator = builder.build()
        return validator(**kwargs)
        
