from whoosh.fields import TEXT, NUMERIC

from . import EncryptedConfigStore

# from .. import fields

# # Boolean,
# # Bytes,
# # Date,
# # DateTime,
# # Email,
# # Enum,
# # Factory,
# # Float,
# # GUID,
# # IPAddress,
# # IPRange,
# # Integer,
# # Json,
# # List,
# # Object,
# # Path,
# # Permission,
# # Port,
# # Secret,
# # Server,
# # String,
# # Tel,
# # Time,
# # Typed,
# # URL,
# # User,
# # UserFactory,
# # UserType,
# # ValidationError,
# # )

# FIELD_MAP = {
#     fields.Boolean: fields.Boolean,
#     fields.Bytes: fields.Bytes,
#     fields.Date: fields.Date,
#     fields.DateTime: fields.DateTime,
#     fields.Email: fields.Email,
#     fields.Enum: fields.Enum,
#     fields.Factory: fields.Factory,
#     fields.Float: fields.Float,
#     fields.GUID: fields.GUID,
#     fields.IPAddress: fields.IPAddress,
#     fields.IPRange: fields.IPRange,
#     fields.Integer: fields.Integer,
#     fields.Json: fields.Json,
#     fields.List: fields.List,
#     fields.Object: fields.Object,
#     fields.Path: fields.Path,
#     fields.Permission: fields.Permission,
#     fields.Port: fields.Port,
#     fields.Secret: fields.Secret,
#     fields.Server: fields.Server,
#     fields.String: fields.String,
#     fields.Tel: fields.Tel,
#     fields.Time: fields.Time,
#     fields.Typed: fields.Typed,
#     fields.URL: fields.URL,
#     fields.User: fields.User,
#     fields.UserFactory: fields.UserFactory,
#     fields.UserType: fields.UserType,
#     fields.ValidationError: fields.ValidationError,
# }


class WhooshStore(EncryptedConfigStore):
    """
    whoosh store is an EncryptedConfigStore

    It saves and indexes the data in a whoosh index
    """

    def __init__(self, location):
        """
        create a new redis store, the location given will be used to generate keys

        this keys will be combined to get/set instance config

        Args:
            location (Location)
        """
        super().__init__(location)
        config = self.config_env.get_store_config("whoosh")
        self.base_index_path = config["path"]

    @property
    def schema(self):
        pass
