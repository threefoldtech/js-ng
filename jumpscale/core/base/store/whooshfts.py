from whoosh import fields
from whoosh.index import create_in, exists_in, open_dir
from whoosh.qparser import FuzzyTermPlugin, GtLtPlugin, MultifieldParser, PhrasePlugin
from whoosh.writing import AsyncWriter

from . import ConfigNotFound, EncryptedConfigStore, KEY_FIELD_NAME
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
    "Path": fields.ID(stored=True),
    "String": fields.TEXT(stored=True),
    "Tel": fields.TEXT(stored=True),
    "URL": fields.TEXT(stored=True),
    "Integer": fields.NUMERIC(bits=64, stored=True, sortable=True),
    "Float": fields.NUMERIC(float, bits=64, stored=True, sortable=True),
    "Port": fields.NUMERIC(stored=True, sortable=True),
    "Date": fields.NUMERIC(stored=True, sortable=True),
    "DateTime": fields.NUMERIC(stored=True, sortable=True),
    "Time": fields.NUMERIC(stored=True, sortable=True),
}

# enums and secret fields are special case,
# for enum, it can be stored as int, bool, or str values...
# so, the field type is selected based on enum values (assuming they're all of the same type)
ENUM_FIELD = "Enum"
# for secret, its field name prefixed with underscores is not valid in whoosh
# they are handled when reading/writing the data
SECRET_FIELD = "Secret"


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

        self.schema = self.get_schema()
        self.index = self.get_index(self.schema)

        self.default_plugins = [FuzzyTermPlugin(), GtLtPlugin(), PhrasePlugin()]
        self.default_pagenum = 1
        self.default_pagelen = 20

    @property
    def index_path(self):
        path = join_paths(self.base_index_path, self.location.name)
        mkdirs(path)
        return path

    @property
    def type_fields(self):
        return self.location.type._fields.items()

    def get_schema(self):
        schema_fields = {
            KEY_FIELD_NAME: fields.ID(unique=True, stored=True),
        }

        for name, field in self.type_fields:
            field_type_name = field.__class__.__name__
            if field_type_name in FIELD_MAP:
                schema_fields[name] = FIELD_MAP[field_type_name]
            elif field_type_name == ENUM_FIELD:
                # it depends on the type of enum values
                enum_value_type = type(field.default)
                if isinstance(enum_value_type, (str, bytes, bytearray)):
                    schema_field = fields.TEXT(stored=True)
                elif isinstance(enum_value_type, (int, float)):
                    schema_field = fields.NUMERIC(stored=True)
                else:
                    schema_field = fields.STORED

                schema_fields[name] = schema_field
            else:
                schema_fields[name] = fields.STORED

        return fields.Schema(**schema_fields)

    def get_index(self, schema):
        if exists_in(self.index_path):
            return open_dir(self.index_path, schema=schema)
        return create_in(self.index_path, schema=schema)

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
            doc = searcher.document(**kw)

            if not doc:
                raise ConfigNotFound(f"cannot find config for {instance_name} in the index")

            for name, field in self.type_fields:
                # whoosh does not store None values, so, we just set them
                # if they are not set, that means when they're added, they'd the value of None
                if name not in doc and field.stored:
                    doc[name] = None

                # add __ to field name by hand
                # as we cannot add a field that starts with "__" in whoosh schema
                if field.__class__.__name__ == SECRET_FIELD:
                    name_with_prefix = f"__{name}"
                    doc[name_with_prefix] = doc[name]
                    doc.pop(name)

            return doc

    def write(self, instance_name, data):
        data[KEY_FIELD_NAME] = instance_name

        for name, field in self.type_fields:
            if field.__class__.__name__ == SECRET_FIELD:
                name_with_prefix = f"__{name}"
                if name_with_prefix in data:
                    # remove "__", as the whoosh field cannot start with it
                    # the original field name is the one used in whoosh schema
                    data[name] = data[name_with_prefix]
                    data.pop(name_with_prefix)

        writer = self.get_writer()
        writer.update_document(**data)
        writer.commit()

    def list_all(self):
        with self.get_reader() as reader:
            for _, doc in reader.iter_docs():
                yield doc[KEY_FIELD_NAME]

    def find(self, cursor_=None, limit_=None, **queries):
        fields = queries.keys()
        query_text = " ".join([f"{field}:{queries[field]}" for field in fields])

        parser = MultifieldParser(fields, schema=self.schema)
        parser.add_plugins(self.default_plugins)

        query = parser.parse(query_text)
        searcher = self.get_searcher()

        if not cursor_:
            cursor_ = self.default_pagenum
        if not limit_:
            limit_ = self.default_pagelen

        result = searcher.search_page(query, pagenum=cursor_, pagelen=limit_)

        if result.is_last_page():
            new_cursor = None
        else:
            new_cursor = result.pagenum + 1

        if result.total >= limit_:
            result = result[:limit_]

        return new_cursor, len(result), (hit for hit in result)

    def delete(self, instance_name):
        writer = self.get_writer()
        writer.delete_by_term(KEY_FIELD_NAME, instance_name)
        writer.commit()
