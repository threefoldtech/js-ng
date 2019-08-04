import tarfile


class Tar(tarfile.TarFile):
    def __init__(self, path):
        self.path = path

    def is_tar(self):
        return tarfile.is_tarfile(self.path)

    def extract(self):
        with tarfile.open(self.path, "r") as file:
            file.extractall()

    def get_content(self):
        with tarfile.open(self.path, "r") as file:
            content = file.getnames()
        return content

    def extract_file(self, file_name):
        with tarfile.open(self.path, "r") as file:
            file.extract(file_name)


def archive(filetar_path, archive_name):
    with tarfile.open(archive_name, "w") as file:
        file.add(filetar_path)
