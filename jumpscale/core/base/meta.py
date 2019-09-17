from collections import namedtuple
from types import SimpleNamespace

from .factory import Factory, DuplicateError
from .fields import Field, Secret, Object, ValidationError


def get_field_property(name, field):
    inner_name = f"__{name}"

    def getter(self):
        return getattr(self, inner_name)

    def setter(self, value):
        if hasattr(value, "validate"):
            value.validate()
        else:
            field.validate(value)
        setattr(self, inner_name, value)
        self._data_updated(name, value)

    return property(fget=getter, fset=setter)


def new_get_factory_info_method(factory_info):
    def _get_factory_info(self):
        return factory_info

    return _get_factory_info


def new_get_fields_method(fields):
    def _get_fields(self):
        return fields

    return _get_fields


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
        new_class._get_fields = new_get_fields_method(fields)
        new_class._get_factory_info = new_get_factory_info_method(factories)
        return new_class


class Base(SimpleNamespace, metaclass=BaseMeta):
    def _get_fields(self):
        return {}

    def _get_embedded_objects(self):
        return [getattr(self, name) for name, field in self._get_fields().items() if isinstance(field, Object)]

    def _get_factory_info(self):
        return []

    def __init__(self):
        for name, field in self._get_fields().items():
            setattr(self, f"__{name}", field.default)

        for info in self._get_factory_info():
            setattr(self, info.name, info.factory(info.type))

    def _get_factories(self):
        return {info.name: getattr(self, info.name) for info in self._get_factory_info()}

    def validate(self):
        for name, field in self._get_fields().items():
            field.validate(getattr(self, name))

    def _get_data(self):
        data = {}

        for name, field in self._get_fields().items():
            value = getattr(self, name)
            if isinstance(field, Secret):
                data[f"__{name}"] = value
            elif isinstance(field, Object):
                data[name] = value._get_data()
            else:
                data[name] = value

        return data

    def _set_data(self, new_data):
        for name, field in self._get_fields().items():
            if name in new_data:
                value = new_data[name]
                try:
                    if isinstance(value, dict):
                        # fields.Object
                        obj = field.type()
                        obj._set_data(value)
                        value = obj
                    setattr(self, f"__{name}", value)
                except ValidationError:
                    pass

    def _data_updated(self, name, value):
        pass

    def _on_data_update(self, name, value):
        pass
