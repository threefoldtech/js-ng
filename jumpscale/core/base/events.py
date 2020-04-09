class InstanceEvent:
    def __init__(self, name, instance=None):
        self.name = name
        self.instance = instance


class AttributeUpdateEvent(InstanceEvent):
    def __init__(self, instance, name, new_value):
        super().__init__(name, instance)
        self.new_value = new_value


class InstanceCreateEvent(InstanceEvent):
    def __init__(self, name, instance):
        super().__init__(instance)
        self.name = name


class InstanceDeleteEvent(InstanceEvent):
    pass
