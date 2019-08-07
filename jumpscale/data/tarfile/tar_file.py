import tarfile
import os


class TarReader:
    def __init__(self, tarfile_path):
        """"
        Args:
            tarfile_path (str) : the path for the tar file.
        """
        self.path = tarfile_path
        self.file = self.__enter__()

    def __enter__(self):
        self.file = tarfile.TarFile.open(self.path, "r")
        return self.file

    def __exit__(self, type, value, traceback):
        self.file.close()

    def extract(self, output):
        """
        extract all the files on the archive to a directory in the path where the tar file is.
        Args:
            output (str) : the path for the output folder
        """
        self.file.extractall(output)

    def get_content(self):
        """
        get the names of all the content in the archive without extraction.
        Returns:
            list of the content
        """

        return self.file.getnames()

    def extract_file(self, file_name):
        """
        extract a specific file on the archive to a directory in the path where the tar file is.
        Args:
            file_name (str) : the name of the file in the archive.
        """
        self.file.extract(file_name)


def istar(path):
    """
    check if the file is an archive or not.
    Returns:
        boolen expresion
    """
    return tarfile.is_tarfile(path)


def archive(source_path, archive_path):
    """
    make an archive from a directory
    Args:
        source_path (str) : the directory will be archived.
        archive_path (str) : where the archive will be stored.
    """
    with tarfile.TarFile.open(archive_path, "w") as file:
        file.add(source_path)
