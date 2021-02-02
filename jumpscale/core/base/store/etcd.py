import etcd3

from . import ConfigNotFound, EncryptedConfigStore
from .serializers import JsonSerializer

class EtcdStore(EncryptedConfigStore):
    pass