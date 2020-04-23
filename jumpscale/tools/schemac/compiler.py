from jumpscale.god import j
import re

from .plugins import CrystalGenerator, JSNGGenerator


ALLOWED_LANGS = {"python": JSNGGenerator, "jsng": JSNGGenerator, "crystal": CrystalGenerator}


def generator_by_name(language_name="python"):
    return ALLOWED_LANGS[language_name]


class Compiler:
    def __init__(self, lang="python", schema_text=""):
        self._schema_text = schema_text
        self.lang = lang = lang
        self._parsed_schemas = {}

    @property
    def generator(self):
        return generator_by_name(self.lang)()

    def parse(self):
        schemas_texts = []
        to_process = self._schema_text
        if to_process.count("@url") == 1:
            schemas_texts = [self._schema_text]
        else:
            urls_positions = [m.start() for m in re.finditer("@url", self._schema_text)]
            urls_positions.append(len(self._schema_text))
            start_end_positions = list(zip(urls_positions, urls_positions[1:]))

            schemas_texts = [self._schema_text[start:end] for (start, end) in start_end_positions]

        parsed_schemas = [j.data.schema.parse_schema(schema_text) for schema_text in schemas_texts]
        self._parsed_schemas = {s.url_to_class_name: s for s in parsed_schemas}

        return self._parsed_schemas
