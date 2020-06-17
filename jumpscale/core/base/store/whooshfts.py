from whoosh import fields
from whoosh.index import create_in, exists_in, open_dir
from whoosh.writing import AsyncWriter

from . import EncryptedConfigStore
from .serializers import Serializer


from jumpscale.sals.fs import join_paths, mkdirs

# a map betwen our indexable fields and whoosh fields
# for now we don't support nested fields like Lists or Objects
# they will only be stored but not indexed
FIELD_MAP = {
    "Boolean": fields.BOOLEAN(stored=True),
    "Bytes": fields.TEXT(stored=True),
    "Email": fields.TEXT(stored=True),
    "GUID": fields.TEXT(stored=True),
    "IPAddress": fields.TEXT(stored=True),
    "IPRange": fields.TEXT(stored=True),
    "Json": fields.TEXT(stored=True),
    "Path": fields.TEXT(stored=True),
    "String": fields.TEXT(stored=True),
    "Tel": fields.TEXT(stored=True),
    "URL": fields.TEXT(stored=True),
    "Integer": fields.NUMERIC(stored=True),
    "Float": fields.NUMERIC(stored=True),
    "Port": fields.NUMERIC(stored=True),
    "Enum": fields.IDLIST(stored=True),
    "Date": fields.NUMERIC(stored=True),
    "DateTime": fields.NUMERIC(stored=True),
    "Time": fields.NUMERIC(stored=True),
}

# we will use this as a key for indexed documents
# will be added for every document
KEY_FIELD_NAME = "instance_name_"


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
        super().__init__(location, Serializer())
        config = self.config_env.get_store_config("whoosh")
        self.base_index_path = config["path"]
        self.index = self.get_index()

    @property
    def index_path(self):
        path = join_paths(self.base_index_path, self.location.name)
        mkdirs(path)
        return path

    @property
    def schema(self):
        type_fields = self.location.type._fields
        schema_fields = {KEY_FIELD_NAME: fields.ID(unique=True, stored=True)}

        for name, field in type_fields.items():
            field_type_name = field.__class__.__name__
            if field_type_name in FIELD_MAP:
                schema_fields[name] = FIELD_MAP[field_type_name]
            else:
                schema_fields[name] = fields.STORED

        return fields.Schema(**schema_fields)

    def get_index(self):
        if exists_in(self.index_path):
            return open_dir(self.index_path)
        return create_in(self.index_path, self.schema)

    def get_reader(self):
        return self.index.reader()

    def get_writer(self):
        return AsyncWriter(self.index)

    def get_searcher(self, up_to_date=True):
        searcher = self.index.searcher()

        if up_to_date and not searcher.up_to_date():
            searcher = searcher.refresh()

        return searcher

    def read(self, instance_name):
        with self.get_searcher() as searcher:
            kw = {KEY_FIELD_NAME: instance_name}
            return searcher.document(**kw)

    def write(self, instance_name, data):
        data[KEY_FIELD_NAME] = instance_name
        writer = self.get_writer()
        writer.update_document(**data)
        writer.commit()

    def list_all(self):
        names = set()
        with self.get_reader() as reader:
            for _, doc in reader.iter_docs():
                names.add(doc[KEY_FIELD_NAME])
        return names

    def find(self, **queries):
        # should search queries by given fields
        # TODO: we need to decide if query will be given by caller/user
        # or we would build it based fields/query mapping given
        pass

    def delete(self, instance_name):
        writer = self.get_writer()
        writer.delete_by_term(KEY_FIELD_NAME, instance_name)
        writer.commit()


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
