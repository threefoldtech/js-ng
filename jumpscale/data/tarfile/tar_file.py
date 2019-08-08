import tarfile


def istar(path):
    """check if the file is .tar format
    
    Arguments:
        path (str) : the path for the file
    """
    return tarfile.is_tarfile(path)


def compress(source, output):
    """make an archive file from directory or file
    
    Arguments:
        source (str) : the path for the file or the directory
        output (str) : the path for the output
    """
    with tarfile.open(output, "w") as output:
        output.add(source)


class Reader:
    """handle the reading operation on tar file
    
    Arguments:
        path (str) : the path for tar file
    """

    def __init__(self, path):

        self.path = path
        self.file = tarfile.TarFile.open(self.path, "r")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()

    def get_content(self):
        """get list of the content in tar file"""
        return self.file.getnames()

    def extract(self, output):
        """extract all the files from the archive to a directory.
        Args:
            output (str) : the path for the output folder
        """
        self.file.extractall(path=output)
