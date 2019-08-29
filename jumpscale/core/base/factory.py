from functools import partial

from .store import FileSystemStore, RedisStore


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

    def _updated(self, new_count):
        pass

    def __get_count(self):
        return self.__count

    def __set_count(self, new_count):
        self.__count = new_count
        self._updated(new_count)

    count = property(__get_count, __set_count)


class StoredFactory(Factory):
    STORE = FileSystemStore

    def __init__(self, type_, parent_name=None):
        super(StoredFactory, self).__init__(type_)
        self._set_parent_name(parent_name)
        if not parent_name:
            self._load()

    def _set_parent_name(self, name):
        self.__parent_name = name

    @property
    def store(self):
        return self.STORE(self.type, self.__parent_name)

    def _save_instance(self, name):
        self.store.save(name, self.get(name)._get_data())

    def _validate_and_save_instance(self, name):
        instance = self.get(name)
        instance._validate()
        self.store.save(name, instance._get_data())

    def _instance_updated(self, name):
        # try to save instance if it's validated
        try:
            self._validate_and_save_instance(name)
        except:
            pass

    def _instance_sub_factory_updated(self, name, new_count):
        self._save_instance(name)

    def _get_sub_factory_location_name(self, parent_name, factory_name):
        return ".".join([self.store.location.name, parent_name, factory_name])

    def new(self, name, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)
        instance._date_updated = partial(self._instance_updated, name)
        instance.save = partial(self._validate_and_save_instance, name)

        for prop_name, factory in instance._get_factories().items():
            factory._set_parent_name(self._get_sub_factory_location_name(name, prop_name))
            factory._updated = partial(self._instance_sub_factory_updated, name)
            factory._load()

        return instance

    def _load(self):
        for name in self.store.list_all():
            instance = self.new(name)
            instance._set_data(self.store.get(name))

    def delete(self, name):
        self.store.delete(name)
        super(StoredFactory, self).delete(name)

    def __iter__(self):
        for value in vars(self).values():
            if isinstance(value, self.type):
                yield value
