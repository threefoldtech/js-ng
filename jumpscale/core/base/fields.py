from .factory import StoredFactory
import re


# TODO: validation/serialization using https://marshmallow.readthedocs.io/en/stable/ or http://alecthomas.github.io/voluptuous/docs/_build/html/index.html


class ValidationError(Exception):
    pass


class Field:
    def __init__(self, default=None, required=False, indexed=False, validators=None, **kwargs):
        self.default = default
        self.required = required
        self.indexed = indexed
        self.kwargs = kwargs

        self.validators = validators
        if self.validators is None:
            self.validators = []

        # self.validate = Schema({

        # })

    def validate(self, value):
        if value is None:
            if self.required:
                raise ValidationError("field is required")
        for validator in self.validators:
            validator(value)


class Typed(Field):
    def __init__(self, type_, **kwargs):
        self.type = type_
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)
        if value is not None:
            if not isinstance(value, self.type):
                raise ValidationError(f"value is not of type {self.type}")


class Boolean(Typed):
    def __init__(self, default=False, **kwargs):
        super().__init__(type_=bool, default=default, **kwargs)


class Integer(Typed):
    def __init__(self, default=0, min=0, **kwargs):
        self.min = 0
        super().__init__(type_=int, default=default, min=min, **kwargs)


class Float(Typed):
    def __init__(self, default=0.0, **kwargs):
        super().__init__(type_=float, default=default, min=min, **kwargs)


class String(Typed):
    def __init__(self, **kwargs):
        super().__init__(type_=str, **kwargs)


class Secret(String):
    pass


class Object(Field):
    def __init__(self, type_, type_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self.type = type_
        self.type_kwargs = type_kwargs

        if self.type_kwargs is None:
            self.type_kwargs = {}

        if not self.default:
            self.default = self.type(**self.type_kwargs)

    def validate(self, value):
        """validate objet of Base

        Args:
            value (Base): object
        """
        super().validate(value)
        value.validate()


class List(Field):
    def __init__(self, field, **kwargs):
        self.field = field
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)

        if value is None:
            value = []

        for item in value:
            self.field.validate(item)


class Email(Field):
    def __init__(self, default="", **kwargs):
        super().__init__(default, **kwargs)
        self.regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def validate(self, value):
        """Check whether provided value is a valid email representation
        Args:
            value (str)
        Returns:
            Boolean expresion"""
        super().validate(value)
        return re.search(self.regex, value) is not None


class Path(Field):
    def __init__(self, default="", **kwargs):
        super().__init__(default, **kwargs)
        self.regex = r"^(/[^/ ]*)+/?$"

    def validate(self, value):
        """Check whether provided value is a valid path representation
        Args:
            value (str)
        Returns:
            Boolean expresion"""
        super().validate(value)
        return re.search(self.regex, value) is not None


class URL(Field):
    def __init__(self, default="", **kwargs):
        super().__init__(default, **kwargs)
        self.regex = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"

    def validate(self, value):
        """Check whether provided value is a valid URL representation
        Args:
            value (str)
        Returbs:
            Boolean expresion"""
        super().validate(value)
        return re.search(self.regex, value) is not None


class Factory(StoredFactory):
    pass
