"""
Hierarchal ConfigurationWe is implemented using Factory

The backend to store configurations
- can be encrypted or plain
- Multiple backends (InMemoryStore, FileSystemStore, RedisStore)

"""
from functools import partial
from jumpscale.core import config, events

from .events import InstanceCreateEvent, InstanceDeleteEvent
from .store import Location, FileSystemStore, RedisStore

STORES = {"filesystem": FileSystemStore, "redis": RedisStore}


class DuplicateError(Exception):
    pass


class Factory:
    def __init__(self, type_, name_=None, parent_instance_=None, parent_factory_=None):
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
        self.__parent_factory = factory

    def new(self, name, *args, **kwargs):
        if not name.isidentifier():
            raise ValueError("{} is not a valid identifier".format(name))

        if self.find(name):
            raise DuplicateError(f"instance with name {name} already exists")

        instance = self.type(*args, **kwargs)
        instance._set_instance_name(name)
        # parent instance of this factory is a parent to all of its instances
        instance._set_parent(self.parent_instance)
        setattr(self, name, instance)

        self.count += 1
        self._created(name, instance)
        return instance

    def find(self, name):
        instance = getattr(self, name, None)
        if instance and not isinstance(instance, self.type):
            raise ValueError("{} is an internal attribute".format(name))
        return instance

    def get(self, name, *args, **kwargs):
        instance = self.find(name)
        if instance:
            return instance
        return self.new(name, *args, **kwargs)

    def delete(self, name):
        self.count -= 1
        if hasattr(self, name):
            delattr(self, name)
        self._deleted(name)

    def _deleted(self, name):
        event = InstanceDeleteEvent(name, instance=None)
        events.notify(event)

    def _created(self, name, instance):
        event = InstanceCreateEvent(name, instance)
        events.notify(event)

    def list_all(self):
        return [name for name, value in self.__dict__ if isinstance(value, self.type)]


class StoredFactory(Factory):
    STORE = STORES[config.get_config()["store"]]

    def __init__(self, type_, name_=None, parent_instance_=None, parent_factory_=None):
        super().__init__(type_, name_=name_, parent_instance_=parent_instance_, parent_factory_=parent_factory_)

        if not parent_instance_:
            self._load()

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

        return Location(*name_list)

    @property
    def store(self):
        return self.STORE(self.location)

    def _validate_and_save_instance(self, name, instance):
        instance.validate()
        self.store.save(name, instance._get_data())

    def _try_save_instance(self, name):
        # try to save instance if it's validated
        instance = self.get(name)
        try:
            self._validate_and_save_instance(name, instance)
        except:
            pass
        return instance

    def _instance_updated(self, name, prop, value):
        """called when data is updated for an instance

        Args:
            name (str): instance name
            prop (str): property/field name
            value (any): updated value
        """
        instance = self._try_save_instance(name)
        instance._on_data_update(prop, value)

    def _instance_sub_factory_updated(self, name, factory, new_count):
        """called when a sub-factory is updated for an instance

        Args:
            name (str): instance name
            factory (fields.Factory): factory field/object
            new_count (int): new count for this factory instance
        """
        self._try_save_instance(name)
        factory._on_update(new_count)

    def _setup_data_handlers(self, name, instance):
        """setup data update and save handlers for a given instance

        Args:
            name (str)
            instance (Base): instance object
        """
        # save method
        instance.save = partial(self._validate_and_save_instance, name, instance)

        # TODO: better use events for data updates
        instance_updated = partial(self._instance_updated, name)
        instance._data_updated = instance_updated
        # for embedded objects too
        for obj in instance._get_embedded_objects():
            obj._data_updated = instance_updated

        return instance

    def _setup_sub_factories(self, name, instance):
        # factories
        # TODO: better use events for factory updates
        for factory in instance._get_factories().values():
            factory._updated = partial(self._instance_sub_factory_updated, name, factory)
            factory._set_parent_factory(self)
            factory._load()

    def new(self, name, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)
        self._setup_data_handlers(name, instance)
        self._setup_sub_factories(name, instance)
        return instance

    def _load(self):
        for name in self.store.list_all():
            instance = self.new(name)
            instance._set_data(self.store.get(name))

    def delete(self, name):
        self.store.delete(name)
        super(StoredFactory, self).delete(name)

    def list_all(self):
        return self.store.list_all()

    def __iter__(self):
        for value in vars(self).values():
            if isinstance(value, self.type):
                yield value
