from .meta import Field
from .factory import StoredFactory

# TODO: validation/serialization using https://marshmallow.readthedocs.io/en/stable/ or http://alecthomas.github.io/voluptuous/docs/_build/html/index.html


class Typed(Field):
    def __init__(self, type_, default=None, indexed=False, required=False, **kwargs):
        self.type = type_
        self.default = default
        self.indexed = indexed

        # self.validate = Schema({

        # })
        super().__init__(default=default, indexed=indexed, **kwargs)

    def validate(self, value):
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


class Factory(StoredFactory):
    pass
