"""
Hierarchal configurations and factories for any `jumpscale.core.base.meta.Base` type/class.

It is implemented using:

- `Factory`: the base for all factories, implements an in-memory factory for any type.
- `StoredFactory`: a factory which stores and load configuration according to the current configured store backend.


Default store configured is file system, you can show current store config by doing:

```
✗ jsctl config get store
store = filesystem
```

Get all stores configurations:

```
✗ jsctl config get stores
redis.hostname = "localhost"
redis.port = 6379
filesystem.path = "/home/abom/.config/jumpscale/secureconfig"
whoosh.path = "/home/abom/.config/jumpscale/whoosh_indexes"
```

For example, set current store to redis:

```
jsctl config update store redis
```

This will use current redis config (hostname: localhost, port: 6379).
"""
from functools import partial
from jumpscale.core import config, events

from .events import InstanceCreateEvent, InstanceDeleteEvent
from .store import ConfigNotFound, KEY_FIELD_NAME, Location
from .store.filesystem import FileSystemStore
from .store.redis import RedisStore
from .store.whooshfts import WhooshStore


STORES = {"filesystem": FileSystemStore, "redis": RedisStore, "whoosh": WhooshStore}


class DuplicateError(Exception):
    """
    raised when you try to create an instance by the same name of an existing one for a factory
    """


class Factory:
    """
    Base factory, where you can create/get/list/delete new instances.

    All of the operations are done in memory, also instances will be available as properties.

    Example:

    ```python

    class Car(Base):
        name = fields.String()
        color = fields.String()

    cars = Factory(Car)
    acar = cars.get("mycar")
    acar.name = "fiat"

    print(cars.mycar.name)
    ```
    """

    def __init__(self, type_, name_=None, parent_instance_=None, parent_factory_=None):
        """
        get a new factory given the type to create instances for.

        Any factory can have a name, parent `Base` instance and a parent factory.

        Args:
            type_ (Base): `Base` class type
            name_ (str, optional): factory name. Defaults to None.
            parent_instance_ (Base, optional): a parent `Base` instance. Defaults to None.
            parent_factory_ (Factory, optional): a parent `Factory`. Defaults to None.
        """
        self.__name = name_
        self.__parent_instance = parent_instance_
        self.__parent_factory = parent_factory_

        self.type = type_
        self.count = 0

    @property
    def parent_instance(self):
        return self.__parent_instance

    @property
    def name(self):
        return self.__name

    @property
    def parent_factory(self):
        return self.__parent_factory

    def _set_parent_factory(self, factory):
        """
        set current parent factory

        Args:
            factory (Factory)
        """
        self.__parent_factory = factory

    def find(self, name):
        """
        find an instance with the given name

        Args:
            name (str): instance name

        Raises:
            ValueError: in case the name is an internal attribute of this factory, like `get` or `new`.

        Returns:
            Base or NoneType: an instance or none
        """
        instance = getattr(self, name, None)
        if instance and not isinstance(instance, self.type):
            raise ValueError("{} is an internal attribute".format(name))
        return instance

    def _create_instance(self, name_, *args, **kwargs):
        """
        create a new instance, this method is only responsible for:

        - validating the name used is correct (must be a valid identifier and does not start with "__")
        - creating the instance from `self.type`
        - setting this instance name with the given name
        - setting the parent instance to it if this factory have a parent instance
        - update the counter and trigger `_created`

        Args:
            name_ (str): instance name

        Raises:
            ValueError: in case the name is not a valid identifier (e.g contains spaces) or starts with "__"

        Returns:
            Base: instance
        """
        if not name_.isidentifier():
            raise ValueError("{} is not a valid identifier".format(name_))

        if name_.startswith("__"):
            raise ValueError("name cannot start with '__'")

        kwargs["instance_name_"] = name_
        kwargs["parent_"] = self.parent_instance
        instance = self.type(*args, **kwargs)

        self.count += 1
        self._created(instance)
        return instance

    def new(self, name, *args, **kwargs):
        """
        get a new instance and make it available as an attribute

        Args:
            name (str): name
            *args: arbitrary arguments passed to the factory `Base` type
            *kwargs: arbitrary keyword arguments passed to the factory `Base` type

        Raises:
            DuplicateError: in case an instance with the same name exists

        Returns:
            Base: instance
        """
        if self.find(name):
            raise DuplicateError(f"instance with name {name} already exists")

        instance = self._create_instance(name, *args, **kwargs)
        setattr(self, name, instance)
        return instance

    def get(self, name, *args, **kwargs):
        """
        get an instance (will create if it does not exist)

        if the instance with `name` exists, `args` and `kwargs` are ignored.

        Args:
            name (str): name
            *args: arbitrary arguments passed to the factory `Base` type
            *kwargs: arbitrary keyword arguments passed to the factory `Base` type

        Raises:
            DuplicateError: in case an instance with the same name exists

        Returns:
            Base: instance
        """
        instance = self.find(name)
        if instance:
            return instance
        return self.new(name, *args, **kwargs)

    def _delete_instance(self, name):
        """
        delete the instance with given name

        here, we only remove the attribute

        Args:
            name (str): instance/attribute name
        """
        if hasattr(self, name):
            delattr(self, name)

    def delete(self, name):
        """
        delete an instance (with its attribute)

        this will update the count and trigger `_deleted`

        Args:
            name (str)
        """
        self.count -= 1
        self._delete_instance(name)
        self._deleted(name)

    def _deleted(self, name):
        """
        called when an instance is deleted, will trigger `InstanceDeleteEvent`

        Args:
            name (name)
        """
        event = InstanceDeleteEvent(name, factory=self)
        events.notify(event)

    def _created(self, instance):
        """
        called when an instance is created, will trigger `InstanceCreateEvent`

        Args:
            instance (Base)
        """
        event = InstanceCreateEvent(instance=instance, factory=self)
        events.notify(event)

    def list_all(self):
        """
        get a set of all instance names

        this only get a list of all properties that are of factory `Base` type.

        Returns:
            set
        """
        names = set()
        for name, value in self.__dict__.items():
            if isinstance(value, self.type) and not name.startswith("__"):
                names.add(name)
        return names


class StoredFactory(events.Handler, Factory):
    """
    Stored factories are a custom type of `Factory`, which uses current configured store backend
    to store all instance configurations.
    """

    STORE = STORES[config.get("store")]

    def __init__(self, type_, name_=None, parent_instance_=None, parent_factory_=None):
        """
        get a new stored factory given the type to create and store instances for.

        Any factory can have a name, parent `Base` instance and a parent factory.

        Once a stored factory is created, it tries to lazy-load all current configuration for given `type_`.

        Args:
            type_ (Base): `Base` class type
            name_ (str, optional): factory name. Defaults to None.
            parent_instance_ (Base, optional): a parent `Base` instance. Defaults to None.
            parent_factory_ (Factory, optional): a parent `Factory`. Defaults to None.
        """
        super().__init__(type_, name_=name_, parent_instance_=parent_instance_, parent_factory_=parent_factory_)
        self.__store = None

        if not parent_instance_:
            # no parent, then load all instance configurations
            # if it's a parent, it should trigger this loading
            self._load()

        # to handle when a parent instance is deleted
        events.add_listenter(self, InstanceDeleteEvent)

        # if we need to always reload the config from store when getting an instance
        self.always_reload = config.get("factory").get("always_reload", False)

    @property
    def parent_location(self):
        if not self.parent_factory:
            raise ValueError("cannot get parent location if parent factory is not set")
        return self.parent_factory.location

    @property
    def location(self):
        """
        get a unique location for this factory

        Returns:
            Location: location object
        """
        name_list = []

        # first, get the location of parent factory if any
        if self.parent_factory:
            name_list += self.parent_location.name_list

        # if we have a parent instance, then this location should be unique
        # for this instance
        if self.parent_instance:
            name_list.append(self.parent_instance.instance_name)

        # if this factory have a name, append it too
        if self.name:
            name_list.append(self.name)

        # then we append the location of the type
        type_location = Location.from_type(self.type)
        name_list += type_location.name_list

        return Location(*name_list, type_=self.type)

    @property
    def store(self):
        if not self.__store:
            self.__store = self.STORE(self.location)
        return self.__store

    def _validate_and_save_instance(self, instance):
        """
        validate and save a given instance to the store

        Args:
            instance (Base)
        """
        instance.validate()
        self.store.save(instance.instance_name, instance._get_data())
        if instance.parent and hasattr(instance.parent, "save"):
            instance.parent.save()

    def handle(self, ev):
        """
        handle when the parent instance is deleted

        Args:
            ev (InstanceDeleteEvent): instance delete event
        """
        # do nothing if this is a root factory
        if not self.parent_instance or not self.parent_factory:
            return

        # handle deletion of children
        if isinstance(ev, InstanceDeleteEvent):
            if ev.factory == self.parent_factory and ev.name == self.parent_instance.instance_name:
                for name in self.list_all():
                    self.delete(name)

    def _load_sub_factories(self, instance):
        """
        load sub-factories for an instance

        this will also set current factory as a parent for any sub-factories this instance have

        Args:
            instance (Base)
        """
        for factory in instance._get_factories().values():
            factory._set_parent_factory(self)
            factory._load()

    def _init_save_and_sub_factories(self, instance):
        """
        allow an instance to have a `save` method

        also, this method inits the loading of sub-factories for this instance

        Args:
            instance (Base)
        """
        instance.save = partial(self._validate_and_save_instance, instance)
        self._load_sub_factories(instance)

    def _get_object_from_config(self, name, data):
        instance = self._create_instance(name, **data)
        self._init_save_and_sub_factories(instance)
        return instance

    def _load_from_store(self, name):
        """
        loads instance from store

        Args:
            name (str): instance name
        Returns:
            Base or NoneType: an instance or none
        """
        try:
            instance_config = self.store.get(name)
        except ConfigNotFound:
            return

        instance = self._get_object_from_config(name, instance_config)
        setattr(self, name, instance)
        return instance

    def find(self, name):
        """
        find an instance with the given name

        Args:
            name (str): instance name

        Raises:
            ValueError: in case the name is an internal attribute of this factory, like `get` or `new`.

        Returns:
            Base or NoneType: an instance or none
        """
        instance = super().find(name)
        if instance:
            if self.always_reload:
                try:
                    instance._set_data(self.store.get(name))
                except ConfigNotFound:
                    # no config is written, still not saved
                    pass
        else:
            instance = self._load_from_store(name)

        return instance

    def new(self, name, *args, **kwargs):
        """
        get a new instance and make it available as an attribute

        this method also initialize sub-factories for this instance.

        Args:
            name (str): name
            *args: arbitrary arguments passed to the factory `Base` type
            *kwargs: arbitrary keyword arguments passed to the factory `Base` type

        Raises:
            DuplicateError: in case an instance with the same name exists

        Returns:
            Base: instance
        """
        instance = super().new(name, *args, **kwargs)
        self._init_save_and_sub_factories(instance)
        return instance

    def get_instance_property(self, name):
        """
        return a new property descriptor for a given name, this will help in lazy-loading
        as this property will only create and load an instance from the store once accessed.

        Args:
            name (str): instance name

        Returns:
            property: property descriptor (object)
        """
        inner_name = f"__{name}"

        def getter(factory):
            # we need to avoid AttributeError which hasattr swallows
            # instead we check the internal __dict__
            if inner_name in factory.__dict__:
                return getattr(factory, inner_name)

            instance = self._get_object_from_config(name, factory.store.get(name))
            setattr(factory, inner_name, instance)
            return instance

        return property(getter)

    def _load(self):
        """
        lazy-load all instance configuration

        it will create a new class for this factory with property descriptors for all instances listed by the store
        """
        # get a new class based on self.__class__
        new_cls = type(self.__class__.__name__, (self.__class__,), {})

        # list all instance names in the store and set a property descriptor as an attribute
        for name in self.store.list_all():
            # it will create the actual instance with configuration from the store when accessed only
            setattr(new_cls, name, self.get_instance_property(name))

        # update current factory class with this class
        self.__class__ = new_cls

    def _delete_instance(self, name):
        """
        delete an instance

        this will delete it from the store too, also, delete its property descriptor if found

        Args:
            name (str): instance name
        """
        self.store.delete(name)

        class_prop = getattr(self.__class__, name, None)
        if isinstance(class_prop, property):
            # created with a property descriptor inside the class, delete it
            delattr(self.__class__, name)

            # check if the instance was actually created or not (if the property was accessed)
            inner_name = f"__{name}"
            if hasattr(self, inner_name):
                # delete the instance itself too if it was accessed and created
                delattr(self, inner_name)
        else:
            super()._delete_instance(name)

    def find_many(self, cursor_=None, limit_=None, **query):
        """
        do a search against the store (not loaded objects) with this query.

        queries can relate to current store backend used.

        Keyword Args:
            cursor_ (any, optional): an optional cursor, to start searching from. Defaults to None.
            limit_ (int, optional): results limit. Defaults to None.
            query: a mapping for field/query, e.g. first_name="aa"

        Returns:
            tuple: the new cursor, total results count, and a list of objects as a result
        """
        if not query:
            raise ValueError("at least one query parameter is required, e.g. age=10")

        new_cursor, count, result = self.store.find(cursor_=cursor_, limit_=limit_, **query)
        return new_cursor, count, (self._get_object_from_config(data[KEY_FIELD_NAME], data) for data in result)

    def list_all(self):
        """
        get all instance names (stored or not)

        Returns:
            set: instance names
        """
        names = set(self.store.list_all())
        return names.union(super().list_all())

    def __iter__(self):
        for value in vars(self).values():
            if isinstance(value, self.type):
                yield value

    def __eq__(self, other):
        return self.location == other.location

    def __hash__(self):
        return hash(self.location)

    def __str__(self):
        """
        readale string for this factory

        Returns:
            str
        """
        return f"{self.__class__.__name__}({self.type.__name__})"

    __repr__ = __str__
