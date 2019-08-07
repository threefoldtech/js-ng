import tempfile
import os.path

from jumpscale.god import j


# def test_archive():
#     sample = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(sample.name, "/tmp/x")
#     assert os.path.isfile("/tmp/x")


# def test_istar():
#     sample = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(sample.name, "/tmp/z")
#     assert j.data.tarfile.istar("/tmp/z")


# def test_get_content():
#     sample = tempfile.NamedTemporaryFile()
#     j.data.tarfile.archive(tmp.name, "/tmp/sample")
#     with j.data.tarfile.TarReader("/tmp/sample") as file:
#         content = file.get_content()
#     assert tmp.name.lstrip("/") in content


# def test_extrect():
#     dir_path = tempfile.mkdtemp()
#     with tempfile.NamedTemporaryFile() as tmp:
#         outpath = os.path.join(dir_path, os.path.basename(tmp.name))
#         j.data.tarfile.archive(tmp.name, outpath)
#     with j.data.tarfile.TarReader(outpath) as tar:
#         tar.extract(dir_path)
#     path = f"{dir_path}{tmp.name}"
#     assert os.path.isfile(path)


def test_extract_file():
    dir_path = tempfile.mkdtemp()
    print(dir_path)
    with tempfile.NamedTemporaryFile() as tmp:
        outpath = os.path.join(dir_path, os.path.basename(tmp.name))
        print(outpath)
        j.data.tarfile.archive(tmp.name, outpath)
    with j.data.tarfile.TarReader(outpath) as tar:
        tar.extract_file(dir_path, tmp.name)
        print(tmp.name)

    # path = f"{dir_path}{tmp.name}"
    # print(path)
    # assert os.path.isfile(path)
    #
