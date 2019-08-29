from .factory import StoredFactory

# TODO: validation/serialization using https://marshmallow.readthedocs.io/en/stable/ or http://alecthomas.github.io/voluptuous/docs/_build/html/index.html


class ValidationError(Exception):
    pass


class Field:
    def __init__(self, default=None, required=False, indexed=False, **kwargs):
        self.default = default
        self.required = required
        self.indexed = indexed
        self.kwargs = kwargs

        # self.validate = Schema({

        # })

    def validate(self, value):
        if value is None:
            if self.required:
                raise ValidationError(f"field is required")


class Typed(Field):
    def __init__(self, type_, **kwargs):
        self.type = type_
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, self.type):
            raise TypeError


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


class Factory(StoredFactory):
    pass
