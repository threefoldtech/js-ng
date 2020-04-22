from jumpscale.god import j


from .plugins import CrystalGenerator, JSNGGenerator


ALLOWED_LANGS = {"python": JSNGGenerator, "jsng": JSNGGenerator, "crystal": CrystalGenerator}


def generator_by_name(language_name="python"):
    return ALLOWED_LANGS[language_name]


class Compiler:
    def __init__(self, lang="python", schema_text=""):
        self._schema_text = schema_text
        self.lang = lang = lang
        self._parsed_schema = None

    @property
    def generator(self):
        return generator_by_name(self.lang)

    def parse(self):
        self._parsed_schema = j.data.schema.parse_schema(self._schema_text)
        return self._parsed_schema

    def generate(self):
        g = self.generator(self._parsed_schema, self._schema_text)
        return g.generate()
