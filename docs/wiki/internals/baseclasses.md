# Base classes

Base classes are intended to provide data modeling, validation and configuration management by utilizing normal python classes. For example, given the following simple class

```python
class Person:
    name = fields.String(default="ahmed")
```

The user should be able to create/store multiple instances of `Person` with valid data.

To achieve this, we implemented base classes using `meta` classes and property descriptors. (a small note, after python `3.7` data classes seems a better option that can be used later).

At first, to explain why we need to implement custom base class/model, we will illustrate the following examples:

If we have the same class called `Person`, with the following definition:


```python
class Person:
    name = fields.String(default="ahmed")
```

Accessing the class variable `name` from class or instance level will yield the same value, an instance of `String` field:

```python
Person.name  #=> <jumpscale.core.base.fields.String object at 0x7efd89980c18>

p = Person()
p.name  #=> <jumpscale.core.base.fields.String object at 0x7efd89980c18>
```

The solution to this problem is using data descriptors (see https://docs.python.org/3/howto/descriptor.html), so the following class:

```python
class Person(Base):
    name = fields.String(default="ahmed")
```

Should have different behavior when accessing `name` from a class or an objects, so, it will be converted by the meta class to a new class like:

```python
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

## BaseMeta

This [metaclass](https://docs.python.org/3/reference/datamodel.html#metaclasses) will convert normal classes to a new class with "injected" properties.

Also, this `metaclass` adds all field information inside `_fields` class variable.


```python
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
        cls_fields = {}
        ...
        ...
```

See complete implementation at [meta.py](https://github.com/threefoldtech/js-ng/blob/fa1582b83c36a8b18094fd208d04499a8d0f289d/jumpscale/core/base/meta.py#L145)


## Base

This base class uses `BaseMeta` as its meta class, hence we have all information about defined fields/properties.

Then it implements
  - Serialization: to_dict/from_dict methods
  - Hierarchy: using an optional `parent_`


See full implementation at [meta.py](https://github.com/threefoldtech/js-ng/blob/fa1582b83c36a8b18094fd208d04499a8d0f289d/jumpscale/core/base/meta.py#L200)

Any one who uses this class as base class/model for his type, he will be able to define [custom fields](https://github.com/threefoldtech/js-ng/blob/development/jumpscale/core/base/fields.py) as class variables, then set/get a serializable and validated data.
