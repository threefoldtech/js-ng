from jumpscale.god import j
import string
import random
from benchmarkit import benchmark, benchmark_run
import pprint

SAVE_PATH = './bcdb_benchmark_time.jsonl'


def generate_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


db = j.data.bcdb.BCDB("load_test")
quotes_model = db.get_model_by_name("quote")

@benchmark(num_iters=1000, save_params=True, save_output=False)
def create_obj():
    obj = quotes_model.create_obj({"author": generate_string(random.randint(1, 20)), "quote": generate_string(random.randint(1, 150))})
    obj.save()


@benchmark(num_iters=10000, save_params=True, save_output=False)
def find_obj():
    quotes_model.get_pattern("quote", generate_string(random.randint(1, 50)))



def run():
    benchmark_results = benchmark_run(
        [create_obj, find_obj],
        SAVE_PATH,
        comment="BCDB benchmark test",
        metric="mean_time",
    )
    return benchmark_results

if __name__ == "__main__":
    pprint.pprint(run())
