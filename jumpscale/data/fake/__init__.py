from faker import Faker
import sys

f = Faker()

sys.modules[__name__] = f