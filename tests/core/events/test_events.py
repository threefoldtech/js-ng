import unittest
from collections import defaultdict

from jumpscale.core import events


class UserHungryEvent:
    def __init__(self, name):
        self.name = name

    def msg(self):
        return f"{self.name} is hungry."


class UserThirstyEvent:
    def __init__(self, name):
        self.name = name

    def msg(self):
        return f"{self.name} is thirsty."


class TestEvents(unittest.TestCase):
    def setUp(self):
        events.listeners[events.Any].clear()
        events.listeners[UserHungryEvent].clear()
        events.listeners[UserThirstyEvent].clear()

    def test_notify_handle_decorators(self):
        notified = defaultdict(list)

        @events.handle_any
        def events_hunger_thirst_logger(ev):
            m = ev.msg()
            notified[ev.__class__].append(events_hunger_thirst_logger)
            print(f"logging from any{m}")

        @events.handle(UserHungryEvent)
        def handle_hungry(ev):
            m = ev.msg()
            notified[ev.__class__].append(handle_hungry)
            print(f"handling event with msg: {m}")

        @events.handle(UserThirstyEvent)
        def handle_thirsty(ev):
            m = ev.msg()
            notified[ev.__class__].append(handle_thirsty)
            print(f"handling thirst with water :d ev with msg: {m}")

        @events.handle_many(UserThirstyEvent, UserHungryEvent)
        def handle_both(ev):
            notified[ev.__class__].append(handle_both)

        ev1 = UserHungryEvent("ahmed")
        ev2 = UserThirstyEvent("dmdm")
        events.notify(ev1)
        events.notify(ev2)

        # handler for any event
        for key, value in notified.items():
            self.assertIn(events_hunger_thirst_logger, value)

        # handles for 1 event
        self.assertIn(handle_hungry, notified.get(UserHungryEvent, []))
        self.assertIn(handle_thirsty, notified.get(UserThirstyEvent, []))

        # handler for multiple events
        self.assertIn(handle_both, notified.get(UserHungryEvent, []))
        self.assertIn(handle_both, notified.get(UserThirstyEvent, []))

    def test_notify_handler(self):
        notified = defaultdict(list)

        class TestHandler(events.Handler):
            def handle(self, ev):
                notified[ev.__class__].append(self)
                print("logging from an event handler object, ", ev.msg())

        handler = TestHandler()
        events.add_listenter(handler, UserHungryEvent)
        events.add_global_listener(handler)

        ev1 = UserHungryEvent("ahmed")
        ev2 = UserThirstyEvent("dmdm")

        events.notify(ev1)
        events.notify(ev2)

        # single event
        self.assertIn(handler, notified.get(UserHungryEvent, []))

        # handler should be found for the other event too (any)
        self.assertIn(handler, notified.get(UserThirstyEvent, []))
