from functools import partial

from jumpscale.data.serializers import json

from .meta import Factory
from .store import FileSystemStore


class StoredFactory(Factory):
    def __init__(self, type_, parent_name=None):
        super(StoredFactory, self).__init__(type_)
        self.parent_name = parent_name
        if not parent_name:
            self.load()

    def set_parent_name(self, name):
        self.parent_name = name

    @property
    def store(self):
        return FileSystemStore(self.type, self.parent_name)

    def save_instance(self, name):
        data = self.get(name).get_data()
        self.store.save(name, json.dumps(data))

    def instance_updated(self, name, prop_name, new_value):
        self.save_instance(name)

    def instance_sub_factory_updated(self, name, new_count):
        self.save_instance(name)

    def new(self, name, *args, **kwargs):
        instance = super().new(name, *args, **kwargs)
        instance.data_updated = partial(self.instance_updated, name)

        for prop_name, factory in instance.get_factories().items():
            factory.set_parent_name(f"{self.type.__name__}_{name}_{prop_name}")
            factory.updated = partial(self.instance_sub_factory_updated, name)
            factory.load()

        return instance

    def load(self):
        for name in self.store.list_all():
            instance = self.new(name)
            instance.set_data(json.loads(self.store.get(name)))

    def delete(self, name):
        self.store.delete(name)
        super(StoredFactory, self).delete(name)

    def __iter__(self):
        for value in vars(self).values():
            if isinstance(value, self.type):
                yield value
