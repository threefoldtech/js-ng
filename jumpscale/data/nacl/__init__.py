from io import BytesIO
from jumpscale.data.serializers.json import dumps
from .jsnacl import *


def payload_build(self, *args):
    """
    build a bytesIO buffer with all arguments serialized to somethign repeatable
    """
    buffer = BytesIO()
    for item in args:
        if not isinstance(item, bytes):
            if isinstance(item, str):
                item = item.encode()
            elif isinstance(item, int) or isinstance(item, float):
                item = str(item).encode()
            elif isinstance(item, dict):
                item = dumps(item).encode()
            else:
                raise ValueError(f"Got {item} supported types are bytes,str,int,float,dict")
        buffer.write(item)
    return buffer.getvalue()
