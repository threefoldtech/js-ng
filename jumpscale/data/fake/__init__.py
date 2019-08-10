from faker import Faker
import sys

f = Faker()

this = sys.modules[__name__]
sys.modules[__name__] = f