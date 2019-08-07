import tempfile
import os.path

from jumpscale.god import j


# def test_archive():
#     sample = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(sample.name, "/tmp/x")
#     assert os.path.isfile("/tmp/x")


def test_istar():
    sample = tempfile.NamedTemporaryFile()
    j.data.tarfile.archive(sample.name, "/tmp/z")
    assert j.data.tarfile.istar("/tmp/z")


# def test_get_content():
#     tmp = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(tmp.name, "/tmp/sample.gz")
#     content = j.data.tarfile.TarReader("/tmp/sample.gz").get_content()
#     assert tmp.name.lstrip("/") in content


# def test_extrect():
#     sample = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(sample.name, "/tmp/xy.gz")
#     with j.data.tarfile.TarReader("/tmp/xy.gz") as f:
#         f.extract("/tmp/xy")
#         assert os.path.isdir("/tmp/xy")


# def test_extract_file():
#     sample = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(sample.name, "/tmp/sample.gz")
#     j.data.tarfile.TarReader("/tmp/sample.gz").extract_file("/tmp/")
#     assert os.path.isdir(f"/tmp/sample")

