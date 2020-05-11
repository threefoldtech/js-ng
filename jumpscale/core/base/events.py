"""
Base and factory related events.
"""


class InstanceEvent:
    def __init__(self, instance=None, factory=None):
        self.instance = instance
        self.factory = factory


class AttributeUpdateEvent(InstanceEvent):
    def __init__(self, instance, name, new_value):
        super().__init__(instance=instance)
        self.name = name
        self.new_value = new_value


class InstanceCreateEvent(InstanceEvent):
    pass


class InstanceDeleteEvent(InstanceEvent):
    def __init__(self, name, instance=None, factory=None):
        super().__init__(instance, factory)
        self.name = name
