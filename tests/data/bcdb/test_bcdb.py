from jumpscale.god import j
from pprint import pprint

# FIXME: re-write this test and add the ability to flush/reset a bcdb instance
# bcdb = j.data.bcdb.BCDB("test")
# emp_model = bcdb.get_model_by_name("employee")
# omar = emp_model.create_obj({"name": "omar", "age": 21, "salary": 1500})
# ahmed = emp_model.create_obj({"name": "ahmed", "age": 30, "salary": 1300})
# emp_model.save_obj(omar)
# emp_model.save_obj(ahmed)
# print("------------------------------------------employee-----------------------------------------------------------")
# print("From 1000 to 1400")
# pprint([emp_model.get_dict(x) for x in emp_model.get_range("salary", 1000, 1400)])
# print("From 1000 to 1600")
# pprint([emp_model.get_dict(x) for x in emp_model.get_range("salary", 1000, 1600)])
# print("From 1300 to 1400")
# pprint([x.get_dict() for x in emp_model.get_range("salary", 1300, 1400)])
# print("------------------------------------------quotes---------------------------------------------------------------")
# quote_model = bcdb.get_model_by_name("quote")
# quote0 = quote_model.create_obj(
#     {
#         "author": "John Keats",
#         "quote": "I love you the more in that I believe you had liked me for my own sake and for nothing else.",
#     }
# )
# quote1 = quote_model.create_obj({"author": "Indira Gandhi", "quote": "You cannot shake hands with a clenched fist."})
# quote2 = quote_model.create_obj(
#     {
#         "author": "Amelia Earhart",
#         "quote": "The most difficult thing is the decision to act, the rest is merely tenacity. The fears are paper tigers. You can do anything you decide to do. You can act to change and control your life; and the procedure, the process is its own reward.",
#     }
# )
# quote3 = quote_model.create_obj({"author": "Leonardo da Vinci", "quote": "Learning never exhausts the mind."})
# quote4 = quote_model.create_obj(
#     {
#         "author": "Francis of Assisi",
#         "quote": "Lord, make me an instrument of thy peace. Where there is hatred, let me sow love.",
#     }
# )
# quote5 = quote_model.create_obj(
#     {"author": "Walt Whitman", "quote": "Keep your face always toward the sunshine - and shadows will fall behind you."}
# )
# quote6 = quote_model.create_obj({"author": "George Orwell", "quote": "Happiness can exist only in acceptance."})
# quote7 = quote_model.create_obj(
#     {"author": "Thomas Jefferson", "quote": "Honesty is the first chapter in the book of wisdom."}
# )
# quote8 = quote_model.create_obj({"author": "Anne Frank", "quote": "Whoever is happy will make others happy too."})
# quote9 = quote_model.create_obj(
#     {"author": "John C. Maxwell", "quote": "A leader is one who knows the way, goes the way, and shows the way."}
# )
# quote10 = quote_model.create_obj({"author": "Milton Berle", "quote": "If opportunity doesn't knock, build a door."})
# quote11 = quote_model.create_obj(
#     {
#         "author": "Plato",
#         "quote": "Wise men speak because they have something to say; Fools because they have to say something.",
#     }
# )
# quote12 = quote_model.create_obj(
#     {"author": "Leo Buscaglia", "quote": "A single rose can be my garden... a single friend, my world."}
# )
# quote13 = quote_model.create_obj(
#     {"author": "Soren Kierkegaard", "quote": "Life is not a problem to be solved, but a reality to be experienced."}
# )
# quote_model.save_obj(quote0)
# quote_model.save_obj(quote1)
# quote_model.save_obj(quote2)
# quote_model.save_obj(quote3)
# quote_model.save_obj(quote4)
# quote_model.save_obj(quote5)
# quote_model.save_obj(quote6)
# quote_model.save_obj(quote7)
# quote_model.save_obj(quote8)
# quote_model.save_obj(quote9)
# quote_model.save_obj(quote10)
# quote_model.save_obj(quote11)
# quote_model.save_obj(quote12)
# quote_model.save_obj(quote13)

# pprint("Quotes that contains the word 'Life'")
# pprint([x.get_dict() for x in quote_model.get_pattern("quote", "decision")])

# pprint("--------------------------------dbs---------------------------------------------")

# db_model = bcdb.get_model_by_name("db")

# redis = db_model.create_obj({"host": "localhost", "user": {"username": "omar", "password": "omar password"}})
# db_model.save_obj(redis)
# retrieved = db_model.get_by("host", "localhost")
# pprint(retrieved.get_dict())

