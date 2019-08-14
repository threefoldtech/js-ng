from types import SimpleNamespace


class DuplicateError(Exception):
    pass


class Factory:
    def __init__(self, type_):
        self.type = type_
        self.__count = 0
        super(Factory, self).__init__()

    def new(self, name, *args, **kwargs):
        if not name.isidentifier():
            raise ValueError("%s is not a valid identifier" % name)

        try:
            self.find(name)
        except AttributeError:
            instance = self.type(*args, **kwargs)
            setattr(self, name, instance)

            self.__count += 1
            return instance

        raise DuplicateError

    def find(self, name):
        instance = getattr(self, name)
        if not isinstance(instance, self.type):
            raise ValueError("%s is an internal attribute" % name)
        return instance

    def get(self, name, *args, **kwargs):
        try:
            return self.find(name)
        except AttributeError:
            return self.new(name, *args, **kwargs)

    def delete(self, name):
        self.__count -= 1
        delattr(self, name)

    def count(self):
        return self.__count


def new_get_fields_method(fields):
    def get_fields(self):
        return fields

    return get_fields


class BaseMeta(type):
    def __new__(cls, name, based, attrs):
        fields = {}
        new_attrs = {}

        for key in attrs:
            obj = attrs[key]
            if isinstance(obj, Factory):
                fields[key] = obj.type
            else:
                new_attrs[key] = obj

        new_class = super(BaseMeta, cls).__new__(cls, name, based, new_attrs)
        new_class.get_fields = new_get_fields_method(fields)
        return new_class


class Base(SimpleNamespace, metaclass=BaseMeta):
    def get_fields(self):
        return {}

    def __init__(self):
        for name, type_ in self.get_fields().items():
            setattr(self, name, Factory(type_))

