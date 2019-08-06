import pytoml
def fancydumps(self, obj, secure=False):
    """
    if secure then will look for key's ending with _ and will use your secret key to encrypt (see nacl client)
    """

    if not j.data.types.dict.check(obj):
        raise j.exceptions.Input("need to be dict")

    keys = [item for item in obj.keys()]
    keys.sort()

    out = ""
    prefix = ""
    lastprefix = ""
    for key in keys:

        val = obj[key]

        # get some vertical spaces between groups which are not equal
        if "." in key:
            prefix, key.split(".", 1)
        # elif "_" in key:
        #     prefix, key.split("_", 1)
        else:
            prefix = key[0:6]

        if prefix != lastprefix:
            out += "\n"
            # print("PREFIXCHANGE:%s:%s" % (prefix, lastprefix))
            lastprefix = prefix
        # else:
        # print("PREFIXNOCHANGE:%s:%s" % (prefix, lastprefix))

        ttype = j.data.types.type_detect(val)
        if secure and key.endswith("_") and ttype.BASETYPE == "string":
            val = j.data.nacl.default.encryptSymmetric(val, hex=True, salt=val)

        out += "%s\n" % (ttype.toml_string_get(val, key=key))

        # else:
        #     raise RuntimeError("error in fancydumps for %s in %s"%(key,obj))

    out = out.replace("\n\n\n", "\n\n")

    return j.core.text.strip(out)

def dumps(self, obj):
    return pytoml.dumps(obj, sort_keys=True)

def loads(self, s, secure=False):
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    try:
        val = pytoml.loads(s)
    except Exception as e:
        raise RuntimeError("Toml deserialization failed for:\n%s.\nMsg:%s" % (j.core.text.indent(s), str(e)))
    if secure and j.data.types.dict.check(val):
        res = {}
        for key, item in val.items():
            if key.endswith("_"):
                res[key] = j.data.nacl.default.decryptSymmetric(item, hex=True).decode()
        val = res
    return val

def merge(
    self,
    tomlsource,
    tomlupdate,
    keys_replace={},
    add_non_exist=False,
    die=True,
    errors=[],
    listunique=False,
    listsort=True,
    liststrip=True,
):
    """
    the values of the tomlupdate will be applied on tomlsource (are strings or dicts)
    @param add_non_exist, if False then will die if there is a value in the dictupdate which is not in the dictsource
    @param keys_replace, key = key to replace with value in the dictsource (which will be the result)
    @param if die=False then will return errors, the list has the keys which were in dictupdate but not in dictsource
    listsort means that items in list will be sorted (list at level 1 under dict)
    @return dict,errors
    """
    if j.data.types.string.check(tomlsource):
        try:
            dictsource = self.loads(tomlsource)
        except Exception:
            raise RuntimeError("toml file source is not properly formatted.")
    else:
        dictsource = tomlsource
    if j.data.types.string.check(tomlupdate):
        try:
            dictupdate = self.loads(tomlupdate)
        except Exception:
            raise RuntimeError("toml file source is not properly formatted.")
    else:
        dictupdate = tomlupdate

    return j.data.serializers.dict.merge(
        dictsource,
        dictupdate,
        keys_replace=keys_replace,
        add_non_exist=add_non_exist,
        die=die,
        errors=errors,
        listunique=listunique,
        listsort=listsort,
        liststrip=liststrip,
    )