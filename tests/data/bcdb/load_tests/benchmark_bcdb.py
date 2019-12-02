from jumpscale.god import j
import string
import random


def generate_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


db = j.data.bcdb.BCDB("load_test")
quotes_model = self.db.get_model_by_name("quote")


def create_obj():
    obj = quotes_model.create_obj({"author": generate_string(random.randint(1, 20)), "quote": generate_string(random.randint(1, 150))})
    obj.save()

def find_obj():
    quotes_model.get_pattern("quote", generate_string(random.randint(1, 50)))



if __name__ == "__main__":
    for i in rane(10000):
        create_obj()
        find_obj()    