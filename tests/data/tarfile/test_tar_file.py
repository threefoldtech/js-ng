import tempfile
import os.path
from jumpscale.loader import j
import pytest


@pytest.fixture
def tear_down(autouse=True):
    yield
    if j.sals.fs.exists("/tmp/x"):
        j.sals.fs.rmtree("/tmp/x")
    if j.sals.fs.exists("/tmp/x.gz"):
        j.sals.fs.rmtree("/tmp/x.gz")


def test_compress(tear_down):
    with tempfile.NamedTemporaryFile() as source:
        j.data.tarfile.compress(source.name, "/tmp/x")
        assert os.path.isfile("/tmp/x")


def test_istar(tear_down):
    with tempfile.NamedTemporaryFile() as source:
        j.data.tarfile.compress(source.name, "/tmp/x")
        assert j.data.tarfile.istar("/tmp/x")


def test_get_content(tear_down):
    with tempfile.NamedTemporaryFile() as foo:
        j.data.tarfile.compress(foo.name, "/tmp/x.gz")
    with j.data.tarfile.Reader("/tmp/x.gz") as tf:
        content = tf.get_content()
        assert foo.name.lstrip("/") in content


def test_extract(tear_down):
    dir_0 = tempfile.mkdtemp()
    out_dir = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(dir=dir_0) as file:
        j.data.tarfile.compress(file.name, "/tmp/x")
    with j.data.tarfile.Reader("/tmp/x") as tar:
        tar.extract(out_dir)
    assert os.path.isdir(f"{out_dir}/tmp")
    j.sals.fs.rmtree(dir_0)
    j.sals.fs.rmtree(out_dir)
