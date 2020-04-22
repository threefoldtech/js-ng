def get_compiler(schema_text, lang="python"):
    from .compiler import Compiler

    return Compiler(lang, schema_text)
