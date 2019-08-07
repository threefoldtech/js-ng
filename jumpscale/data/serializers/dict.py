import copy


def _unique_list(items, sort=False, strip=False):
    res = []
    for item in items:
        if strip and isinstance(item, str):
            item = item.strip()
        if item not in res:
            res.append(item)
    if sort:
        res.sort()
    return res


def set_value(
    dictsource, key, val, add_non_exist=False, die=True, errors=[], listunique=False, listsort=True, liststrip=True
):
    """
    start from a dict template (we only go 1 level deep)
    will check the type & corresponding the type fill in
    @return dict,errors=[]
    in errors is list of list [[key,val],...]
    """
    if key not in dictsource.keys():
        if add_non_exist:
            dictsource[key] = val
            return dictsource, errors
        else:
            if die:
                raise Exception("dictsource does not have key:%s, can insert value" % key)
            else:
                errors.append((key, val))
                return dictsource, errors

    if isinstance(dictsource[key],list):
        # check is list & set the types accordingly
        if isinstance(val,str):
            if "," in val:
                val = [item.replace("'", "").strip() for item in val.split(",")]
            else:
                val = [val]
        elif isinstance(val,int) or isinstance(val,float):
            val = [val]

        if listunique:
            dictsource[key] = _unique_list(val, sort=listsort, strip=liststrip)
        else:
            dictsource[key] = val

    elif isinstance(dictsource[key],bool):
        if str(val).lower() in ["true", "1", "y", "yes"]:
            val = True
        else:
            val = False
        dictsource[key] = val
    elif isinstance(dictsource[key],int):
        if isinstance(val,str) and val.strip() == "":
            val = 0
        try:
            dictsource[key] = int(val)
        except ValueError:
            raise ValueError('Expected value of "{}" should be of type int or a string of int.'.format(key))
    elif isinstance(dictsource[key],float):
        try:
            dictsource[key] = float(val)
        except ValueError:
            raise ValueError('Expected value of "{}" should be of type float or a string of float.'.format(key))
    elif isinstance(dictsource[key],str):
        if not isinstance(val,str):
            raise ValueError('Expected value of "{}" should be of type string.'.format(key))
        dictsource[key] = str(val).strip()
    else:
        raise ValueError("could not find type of:%s" % dictsource[key])

    return dictsource, errors


def merge(
    dictsource={},
    dictupdate={},
    keys_replace={},
    add_non_exist=False,
    die=True,
    errors=[],
    listunique=False,
    listsort=True,
    liststrip=True,
):
    """
    the values of the dictupdate will be applied on dictsource (can be a template)
    @param add_non_exist, if False then will die if there is a value in the dictupdate which is not in the dictsource
    @param keys_replace, key = key to replace with value in the dictsource (which will be the result)
    @param if die=False then will return errors, the list has the keys which were in dictupdate but not in dictsource
    @return dictsource,errors
    """
    if not isinstance(dictsource,dict) or not isinstance(dictupdate,dict):
        raise Exception("dictsource and dictupdate need to be dicts")

    keys = [item for item in dictupdate.keys()]
    keys.sort()

    dictsource = copy.copy(dictsource)  # otherwise template gets changed

    for key in keys:
        val = dictupdate[key]
        if key in keys_replace.keys():
            key = keys_replace[key]
        dictsource, errors = set_value(
            dictsource,
            key,
            val,
            add_non_exist=add_non_exist,
            die=die,
            errors=errors,
            listunique=listunique,
            listsort=listsort,
            liststrip=liststrip,
        )
    return dictsource, errors
