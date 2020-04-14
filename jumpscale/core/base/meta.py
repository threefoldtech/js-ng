from types import SimpleNamespace

from jumpscale.core import events

from . import fields
from .factory import Factory, StoredFactory, DuplicateError
from .events import AttributeUpdateEvent


def get_field_property(name, field):
    inner_name = f"__{name}"

    def getter(self):
        if hasattr(self, inner_name):
            return getattr(self, inner_name)

        # accept raw value as default too
        return field.from_raw(field.default)

    def setter(self, value):
        if field.readonly:
            raise fields.ValidationError(f"'{name}' is a read only attribute")

        # accept if this is a raw value too
        value = field.from_raw(value)

        # validate
        field.validate(value)

        # set parent
        if isinstance(field, fields.Object):
            value.parent = self

        # se attribute
        setattr(self, inner_name, value)
        self._attr_updated(name, value)

    return property(fget=getter, fset=setter)


class BaseMeta(type):
    def __new__(cls, name, based, attrs):
        """
        get a new class with all fields set in _fields, including base/super class fields too.

        Args:
            name (str): class name
            based (tuple): super class types (classes)
            attrs (dict): current attributes

        Returns:
            any: a new class
        """
        cls_fields = {}
        super_fields = {}

        for super_cls in based:
            if hasattr(super_cls, "_fields"):
                super_fields.update(super_cls._fields)

        # update current attrs with super class fields
        attrs.update(super_fields)

        new_attrs = {}
        for key in attrs:
            obj = attrs[key]
            if isinstance(obj, fields.Field):
                cls_fields[key] = obj
                new_attrs[key] = get_field_property(key, obj)
            else:
                new_attrs[key] = obj

        new_class = super(BaseMeta, cls).__new__(cls, name, based, new_attrs)
        new_class._fields = cls_fields
        return new_class


class Base(SimpleNamespace, metaclass=BaseMeta):
    def __init__(self, parent_=None, instance_name_=None, **values):
        self.__parent = parent_
        self.__instance_name = instance_name_

        self._factories = {}

        for name, field in self._get_fields().items():
            if isinstance(field, fields.Factory):
                value = field.factory_type(field.type, name_=name, parent_instance_=self)
                self._factories[name] = value
            else:
                value = values.get(name, field.from_raw(field.default))

            # accept raw as a default value
            # and set inner value
            setattr(self, f"__{name}", value)

    def _get_fields(self):
        return self._fields

    def _get_factories(self):
        return self._factories

    def _get_embedded_objects(self):
        return [getattr(self, name) for name, field in self._get_fields().items() if isinstance(field, fields.Object)]

    def _get_data(self):
        data = {}

        for name, field in self._get_fields().items():
            if isinstance(field, fields.Factory):
                # skip for factories for now
                continue
            value = getattr(self, name)
            raw_value = field.to_raw(value)
            if isinstance(field, fields.Secret):
                data[f"__{name}"] = raw_value
            else:
                data[name] = raw_value

        return data

    def _set_data(self, new_data):
        for name, field in self._get_fields().items():
            if name in new_data:
                try:
                    setattr(self, f"__{name}", field.from_raw(new_data[name]))
                except (fields.ValidationError, ValueError):
                    # should at least log validation and value errors
                    # this can happen in case of e.g. fields type change
                    pass

    def _attr_updated(self, name, value):
        event = AttributeUpdateEvent(self, name, value)
        events.notify(event)

    def validate(self):
        for name, field in self._get_fields().items():
            field.validate(getattr(self, name))

    @property
    def parent(self):
        return self.__parent

    def _set_parent(self, parent):
        self.__parent = parent

    @property
    def instance_name(self):
        return self.__instance_name

    def _set_instance_name(self, name):
        self.__instance_name = name
