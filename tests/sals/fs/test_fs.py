import pytest
import tempfile
import os
import jumpscale.god as j

def test_copy_file():
    old_folder_path=tempfile.mkdtemp()
    new_folder_path=tempfile.mkdtemp()
    f=tempfile.NamedTemporaryFile(dir=old_folder_path)
    
    