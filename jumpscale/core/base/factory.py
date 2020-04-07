from functools import partial

from jumpscale.core import config

from .store import FileSystemStore, RedisStore

STORES = {"filesystem": FileSystemStore, "redis": RedisStore}


class DuplicateError(Exception):
    pass


class Factory:
    def __init__(self, type_, parent=None):
        self.type = type_
        self.parent = parent
        self.__count = 0

    def new(self, name, *args, **kwargs):
        if not name.isidentifier():
            raise ValueError("{} is not a valid identifier".format(name))

        try:
            self.find(name)
        except AttributeError:
            instance = self.type(*args, **kwargs)
            instance.parent = self.parent
            setattr(self, name, instance)

            self.count += 1
            return instance

        raise DuplicateError

    def find(self, name):
        instance = getattr(self, name)
        if not isinstance(instance, self.type):
            raise ValueError("{} is an internal attribute".format(name))
        return instance

    def get(self, name, *args, **kwargs):
        try:
            return self.find(name)
        except AttributeError:
            return self.new(name, *args, **kwargs)

    def delete(self, name):
        self.count -= 1
        if hasattr(self, name):
            delattr(self, name)

    def _updated(self, new_count):
        pass

    def _on_update(self, new_count):
        pass

    def __get_count(self):
        return self.__count

    def __set_count(self, new_count):
        self.__count = new_count
        self._updated(new_count)

    count = property(__get_count, __set_count)


class StoredFactory(Factory):
    STORE = STORES[config.get_config()["store"]]

    def __init__(self, type_, parent_name=None):
        super(StoredFactory, self).__init__(type_)
        self._set_parent_name(parent_name)
        if not parent_name:
            self._load()

    def _set_parent_name(self, name):
        self.__parent_name = name

    @property
    def parent_name(self):
        return self.__parent_name

    @property
    def store(self):
        return self.STORE(self.type, self.__parent_name)

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

    def _get_sub_factory_location_name(self, parent_name, factory_name):
        return ".".join([self.store.location.name, parent_name, factory_name])

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
        for prop_name, factory in instance._get_factories().items():
            factory._set_parent_name(self._get_sub_factory_location_name(name, prop_name))
            factory.parent = instance
            factory._updated = partial(self._instance_sub_factory_updated, name, factory)
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
