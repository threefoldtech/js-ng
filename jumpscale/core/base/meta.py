from collections import namedtuple
from types import SimpleNamespace


class DuplicateError(Exception):
    pass


class ValidationError(Exception):
    pass


class Field:
    def __init__(self, **kwargs):
        self.default = None
        self.required = False
        self.kwargs = kwargs

    def validate(self, value):
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

            self.count += 1
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
        self.count -= 1
        delattr(self, name)

    def updated(self, new_count):
        pass

    def get_count(self):
        return self.__count

    def set_count(self, new_count):
        self.__count = new_count
        self.updated(new_count)

    count = property(get_count, set_count)


def get_field_property(name, field):
    inner_name = f"__{name}"

    def getter(self):
        return getattr(self, inner_name)

    def setter(self, value):
        if value is None:
            if field.required:
                raise ValidationError(f"{name} is required")
        else:
            field.validate(value)

        setattr(self, inner_name, value)
        self.data_updated(name, value)

    return property(fget=getter, fset=setter)


def new_get_factory_info_method(factory_info):
    def get_factory_info(self):
        return factory_info

    return get_factory_info


def new_get_fields_method(fields):
    def get_fields(self):
        return fields

    return get_fields


FactoryInfo = namedtuple("FactoryInfo", ["name", "type", "factory"])


# TODO: split fields meta and factoreis meta (more clean) or create a generic one  (with different type handlers for fields and factories)


class BaseMeta(type):
    def __new__(cls, name, based, attrs):
        factories = []
        fields = {}
        new_attrs = {}

        for key in attrs:
            obj = attrs[key]
            if isinstance(obj, Factory):
                factory = type(obj)
                factories.append(FactoryInfo(key, obj.type, factory))
            elif isinstance(obj, Field):
                fields[key] = obj
                new_attrs[key] = get_field_property(key, obj)
            else:
                new_attrs[key] = obj

        new_class = super(BaseMeta, cls).__new__(cls, name, based, new_attrs)
        new_class.get_fields = new_get_fields_method(fields)
        new_class.get_factory_info = new_get_factory_info_method(factories)
        return new_class


class Base(SimpleNamespace, metaclass=BaseMeta):
    def get_fields(self):
        return {}

    def get_factory_info(self):
        return []

    def __init__(self):
        for name, field in self.get_fields().items():
            setattr(self, f"__{name}", field.default)

        for info in self.get_factory_info():
            setattr(self, info.name, info.factory(info.type))

    def get_factories(self):
        return {info.name: getattr(self, info.name) for info in self.get_factory_info()}

    def get_data(self):
        return {name: getattr(self, name) for name in self.get_fields().keys()}

    def set_data(self, new_data):
        for name in self.get_fields().keys():
            if name in new_data:
                try:
                    setattr(self, name, new_data[name])
                except Exception:  # should be ValidationError
                    pass

    def data_updated(self, name, value):
        pass
