"""
Meta and Base classes for any class with fields.

Contains mainly:

- `BaseMeta`: A meta class to get a new class with field property descriptors ready
- `Base`: The base class which can be used to get/set current field values


To explain what it does, we will illustrate the following examples:

If we have a class called `Person`, with the following definition:


```python
class Person:
    name = fields.String(default="ahmed")
```

Accessing name from class or instance level will yield the same value, an instance of `String` field:

```python
Person.name  #=> <jumpscale.core.base.fields.String object at 0x7efd89980c18>

p = Person()
p.name  #=> <jumpscale.core.base.fields.String object at 0x7efd89980c18>
```

The solution to this problem is using data descriptors (see https://docs.python.org/3/howto/descriptor.html)

In meta and base implementations, we use property data descriptors, so the following class:

```python
class Person(Base):
    name = fields.String(default="ahmed")
```

Should have different behavior when accessing `name` from a class or an objects, so, it will be converted by meta class to a class like:

```
class Person(Base):
    def __init__(self):
        self.__name = "ahmed"

    @property
    def get_name(self):
        return self.__name

    @property
    def set_name(self, value):
        self.__name == value

    name = property(get_name, set_name)
```

And accessing `name` from class and object levels will yield:

```python
Person.name  #=> <property object at 0x7efd89a259f8>


p = Person()
p.name  #=> "ahmed"
```


Parent relationship is supported too, every instance can have a parent object (which must be a `Base` type too)
"""
from types import SimpleNamespace

from jumpscale.core import events

from . import fields
from .factory import Factory, StoredFactory, DuplicateError
from .events import AttributeUpdateEvent


def get_field_property(name: str, field: fields.Field) -> property:
    """
    get a new property descriptor object for a field,
    this property will be used to enable getting/setting the actual value

    as the field only describes the type and other validation/conversion options,
    but do not hold the value itself, the vale will be held in the base instance

    the getter and setter will be called when an object is already created,
    and any field is accessed:

    ```python
    car = Car()
    print(car.color)  #=> getter will be called
    car.color = "red"  #=> setter will be called
    ```

    Args:
        name (str): field name
        field (fields.Field): field instance

    Returns:
        property: property descriptor (object)
    """

    def getter(self):
        """
        getter method this property

        will call `_get_value`, which would if the value is already defined
        and will get the default value if not

        Returns:
            any: the field value
        """
        return self._get_value(name, field)

    def setter(self, value):
        """
        a setter method for this property

        will call _set_value, which would do some checks:

        - validation: using field.validate_with_name
        - setting an attribute with inner_name in the base instance

        if it's set correctly, we will:

        - call `_attr_updated` of `self` with the name of this `field`
        - call `on_update` of the `field` with `self`

        Args:
            value (any): a value to be set for this field

        Raises:
            fields.ValidationError: in case the value is not valid
        """
        self._set_value(name, field, value)

        # call _attr_updated and on_update handlers
        self._attr_updated(name, value)
        if field.trigger_updates:
            field.on_update(self, value)

    return property(fget=getter, fset=setter)


class BaseMeta(type):
    """
    this class is used to get a new class with all field attributes replaced by property data descriptors.

    this should be used as a metaclass, example:

    ```python
    class ExampleWithFields(metaclass=BaseMeta):
        name = fields.String()
    ```
    """

    def __new__(cls, name: str, based: tuple, attrs: dict) -> type:
        """
        get a new class with all field attributes replaced by property data descriptors.

        Args:
            name (str): class name
            based (tuple): super class types (classes)
            attrs (dict): current attributes

        Returns:
            type: a new class
        """
        # will collect class fields
        # and also all fields of super classes, as we already have them in based
        cls_fields = {}
        super_fields = {}

        for super_cls in based:
            if hasattr(super_cls, "_fields"):
                super_fields.update(super_cls._fields)

        # update current attrs with super class fields
        attrs.update(super_fields)

        # now we maintain old attributes, but convert any attribute
        # with fields.Field type to property descriptor (property object)
        # using get_field_property
        new_attrs = {}
        for key in attrs:
            obj = attrs[key]
            if isinstance(obj, fields.Field):
                cls_fields[key] = obj
                new_attrs[key] = get_field_property(key, obj)
            else:
                # keep other attrs
                new_attrs[key] = obj

        new_class = super(BaseMeta, cls).__new__(cls, name, based, new_attrs)
        # set _fields attributes to cls_fields dict, so, we still have access to field objects
        new_class._fields = cls_fields
        return new_class


class Base(SimpleNamespace, metaclass=BaseMeta):
    def __init__(self, parent_=None, instance_name_=None, **values):
        """
        base class implementation for any class with fields which supports getting/setting raw data for any instance fields.

        any instance can have an optional name and a parent.

        ```python
        class Person(Base):
            name = fields.String()
            age = fields.Float()

        p = Person(name="ahmed", age="19")
        print(p.name, p.age)
        ```

        Args:
            parent_ (Base, optional): parent instance. Defaults to None.
            instance_name_ (str, optional): instance name. Defaults to None.
            **values: any given field values to initiate the instance with
        """
        self.__parent = parent_
        self.__instance_name = instance_name_

        self._factories = {}

        # now we create factories
        for name, field in self._get_fields().items():
            if isinstance(field, fields.Factory):
                value = field.factory_type(field.type, name_=name, parent_instance_=self)
                self._factories[name] = value
                setattr(self, f"__{name}", value)
                # if provided in values, remove it, as it's not needed
                if name in values:
                    values.pop(name)

        # setting other values
        self._set_data(values)

    def _get_fields(self):
        """
        get current defined field objects

        Returns:
            dict: fields dict as {name: field object}
        """
        return self._fields

    def _get_computed_fields(self):
        """
        get current defined field objects with compute function

        Returns:
            dict: fields dict as {name: field object}
        """
        return {name: field for name, field in self._fields.items() if field.computed}

    def _get_factories(self):
        """
        get sub-factory objects, which are defined by `fields.Factory`

        Returns:
            dict: factories as {name: factory object}
        """
        return self._factories

    def _get_embedded_objects(self):
        """
        get a list of embedded objects which are defined by `fields.Object`

        Returns:
            list: list of `Base` objects
        """
        return [getattr(self, name) for name, field in self._get_fields().items() if isinstance(field, fields.Object)]

    def _get_value(self, name, field):
        """
        get a field value

        Args:
            name (str): field name
            field (fields.Field): field object

        Returns:
            any: field value
        """
        # if computed, return the computed value
        if field.computed:
            return field.compute(self)

        # if it's already defined, just return it
        # we don't use hasattr here, because it uses getattr inside
        # it causes an infinite recursion here if the attr is not found
        # and also when __getattr__ is overridden
        inner_name = f"__{name}"
        if inner_name in self.__dict__:
            return getattr(self, inner_name)

        # if default is callable, get it
        if callable(field.default):
            default = field.default()
        else:
            default = field.default

        # use the actual name (not inner_name) to do validation and conversion...etc
        self._set_value(name, field, default)
        return self._get_value(name, field)

    def _set_value(self, name, field, value):
        """
        set a field value

        Args:
            name (str): field name
            field (fields.Field): field object
            value (any): value

        Raises:
            fields.ValidationError: raised if the value is not valid
        """
        if field.readonly:
            raise fields.ValidationError(f"'{name}' is a read only attribute")

        # accept if this is a raw value too
        value = field.from_raw(value)

        # validate
        field.validate_with_name(value, name)

        # set current instance as parent for embedded objects/instances
        if isinstance(field, fields.Object) and value:
            value._set_parent(self)

        # set as an internal attribute
        inner_name = f"__{name}"
        setattr(self, inner_name, value)

    def _get_data(self):
        """
        get a serializable dict from all values of all fields (except factories)

        ```python
        class Person(Base):
            name = fields.String()
            age = fields.Float()

        p = Person(name="ahmed", age=1.4)
        p._get_data()  #=> {'name': 'ahmed', 'age': '19'}
        p.to_dict() #=> {'name': 'ahmed', 'age': '19'}
        ```

        Returns:
            dict: data as dict with {name: value}
        """
        data = {}

        for name, field in self._get_fields().items():
            if isinstance(field, fields.Factory):
                # skip for factories for now
                continue
            if not field.stored:
                # skip non-stored fields too
                continue

            value = self._get_value(name, field)
            raw_value = field.to_raw(value)
            if isinstance(field, fields.Secret):
                data[f"__{name}"] = raw_value
            else:
                data[name] = raw_value

        return data

    def _set_data(self, new_data):
        """
        set values from dict to all fields (except factories)

        Args:
            new_data (dict): field values mapping
        """
        all_fields = self._get_fields()

        for name, value in new_data.items():
            if name in all_fields:
                try:
                    self._set_value(name, all_fields[name], value)
                except (fields.ValidationError, ValueError):
                    # should at least log validation and value errors
                    # this can happen in case of e.g. fields type change
                    pass

    def _attr_updated(self, name, value):
        """
        called when an attribute value is updated

        Args:
            name (str): attribute/field name
            value (any): value
        """
        event = AttributeUpdateEvent(self, name, value)
        events.notify(event)

    def validate(self):
        """
        validate all fields of current instance
        """
        for name, field in self._get_fields().items():
            field.validate_with_name(getattr(self, name), name)

    @property
    def parent(self):
        return self.__parent

    def _set_parent(self, parent):
        """
        set current parent instance

        Args:
            parent (Base): base object/instance
        """
        self.__parent = parent

    @property
    def instance_name(self):
        return self.__instance_name

    def _set_instance_name(self, name):
        """
        set current instance name

        Args:
            name (str): name
        """
        self.__instance_name = name

    to_dict = _get_data

    @classmethod
    def from_dict(cls, data):
        """
        get an instance from a dict

        ```python
        class Person(Base):
            name = fields.String()
            age = fields.Float()

        p = Person.from_dict({"name": "ahmed", "age": 19})
        print(p.name, p.age)  #=> ahmed 19
        ```

        Args:
            data (dict): values dict

        Returns:
            Base: an instance from current `Base` type
        """
        return cls(**data)

    def __eq__(self, other):
        """
        compare self to `other`, which must be of the same type.

        this just compares the data of two objects.

        Args:
            other (Base): other object of the same type of `self`

        Returns:
            bool: `True` if equal, `False` otherwise
        """
        return type(self) == type(other) and self.to_dict() == other.to_dict()

    def __str__(self):
        """
        construct a readable string of base objects as  key-value list

        example:

        ```python
        print(j.servers.openresty.tttt.websites.test.locations.l)
        ```

        output:

        ```
        Location(
            instance_name='l',
            parent=Website(instance_name_='test'),
            name=None,
            path_url='/',
            is_auth=False,
            force_https=False,
            ...
        )
        ```

        Returns:
            str: readable string
        """
        data = {}

        if self.instance_name:
            data["instance_name"] = self.instance_name.__repr__()

        if self.parent and self.parent.instance_name:
            parent_instance_name = self.parent.instance_name.__repr__()
            data["parent"] = f"{self.parent.__class__.__name__}(instance_name_={parent_instance_name})"

        for name, field in self._get_fields().items():
            data[name] = self._get_value(name, field).__repr__()

        values = ",\n".join([f"  {name}={value}" for name, value in data.items()])
        return f"{self.__class__.__name__}(\n{values}\n)"

    __repr__ = __str__
