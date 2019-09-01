from jumpscale.core.base import StoredFactory
from .s3 import S3Client


export_module_as = StoredFactory(S3Client)
