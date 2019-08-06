import tarfile


class Tar(tarfile.TarFile):
    def __init__(self, tarfile_path):
        """"
        Args:
            path (str) : the path for the tar file.
        """
        self.path = tarfile_path

    def is_tar(self):
        """
        check if the file is an archive or not.
        Return:
            boolen expresion
        """
        return tarfile.is_tarfile(self.path)

    def extract(self):
        """
        extract all the files on the archive to a directory in the path where the tar file is.
        """
        with tarfile.open(self.path, "r") as file:
            file.extractall()

    def get_content(self):
        """
        get the names of all the content in the archive without extraction.
        Returns:
            list of the content
        """
        with tarfile.open(self.path, "r") as file:
            content = file.getnames()
        return content

    def extract_file(self, file_name):
        """
        extract a specific file on the archive to a directory in the path where the tar file is.
        Args:
            file_name (str) : the name of the file in the archive.
        """
        with tarfile.open(self.path, "r") as file:
            file.extract(file_name)


def archive(source, archive_name):
    """
    make an archive from a directory
    Args:
        source (str) : the directory will be archived.
        archive_name (str) : the name of the new archive.
    """
    with tarfile.open(archive_name, "w") as file:
        file.add(source)
