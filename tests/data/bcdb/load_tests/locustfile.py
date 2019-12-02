from jumpscale.god import j
from locust import Locust, TaskSet, task, between, seq_task
import string
import random

def generate_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


class UserBehavior(TaskSet):
    def on_start(self):
        self.db = j.data.bcdb.BCDB("load_test")
        self.quotes_model = self.db.get_model_by_name("quote")
    
    def on_stop(self):
        # flush the db
        pass
    
    @seq_task(1)
    def create_obj(self):
        quote = self.quotes_model.create_obj({"author": generate_string(random.randint(1, 20)), "quote": generate_string(random.randint(1, 150))})
        quote.save()
    
    
    @seq_task(2)
    def search_obj(self):
        self.quotes_model.get_pattern("quote", generate_string(random.randint(1, 50)))


class JSUser(Locust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)