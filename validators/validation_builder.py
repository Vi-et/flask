class ValidationBuilder:
    def __init__(self):
        self.rules = []
        self.errors = []

    def build(self):
        """Build the validation function"""

        def validator(**kwargs):
            for rule in self.rules:
                rule(kwargs)

        return validator


class BaseValidation:
    _builder = ValidationBuilder()

    @classmethod
    def validate(cls, **kwargs):
        cls._builder.errors = []  # Reset errors
        validator = cls._builder.build()
        validator(**kwargs)
        return {
            "is_valid": len(cls._builder.errors) == 0,
            "errors": cls._builder.errors,
            "first_error": cls._builder.errors[0] if cls._builder.errors else None,
        }
