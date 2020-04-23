from jumpscale.god import j


def test_schema():
    definition = """
    @url = despiegk.test
    llist = []
    llist2 = "" (LS) #L means = list, S=String
    llist3     = [1,2,3] (LF)
    &nr    = 4


    obj = (O)!7mada.test
    
    date_start = 0 (I)
    
    description* = "hello world"        
    description2 ** = 'creature asd"asd ,xzc'(S)
    llist4*** = [1,2,3] (LI)
    llist5 = [1,2,3] (LI)
    llist6 = [1,2,3] (LI)
    U = 0.0
    nrdefault = 0
    nrdefault2 = (I)
    nrdefault3 = 0 (I)
    """
    schema = j.data.schema.parse_schema(definition)
    assert schema.url == "despiegk.test"
    assert schema.system_props == {"url": "despiegk.test"}
    assert "llist" in schema.props
    assert (
        isinstance(schema.props["llist"].type, j.data.types.List)
        and isinstance(schema.props["llist"].type.subtype, j.data.types.String)
        and schema.props["llist"].type.default == []
    )
    del schema.props["llist"].type
    assert schema.props["llist"].__dict__ == {
        "defaultvalue": "[]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist",
    }
    assert "llist2" in schema.props
    assert (
        isinstance(schema.props["llist2"].type, j.data.types.List)
        and isinstance(schema.props["llist2"].type.subtype, j.data.types.String)
        and schema.props["llist2"].type.default == []
    )
    del schema.props["llist2"].type
    assert schema.props["llist2"].__dict__ == {
        "defaultvalue": "",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "L means = list, S=String",
        "name": "llist2",
    }
    assert "llist3" in schema.props
    assert (
        isinstance(schema.props["llist3"].type, j.data.types.List)
        and isinstance(schema.props["llist3"].type.subtype, j.data.types.Float)
        and schema.props["llist3"].type.default == [1, 2, 3]
    )
    del schema.props["llist3"].type
    assert schema.props["llist3"].__dict__ == {
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist3",
    }
    assert "nr" in schema.props
    assert isinstance(schema.props["nr"].type, j.data.types.Integer) and schema.props["nr"].type.default == 4
    del schema.props["nr"].type
    assert schema.props["nr"].__dict__ == {
        "defaultvalue": "4",
        "index": True,
        "index_key": False,
        "index_text": False,
        "unique": True,
        "comment": "",
        "name": "nr",
    }
    assert "date_start" in schema.props

    assert (
        isinstance(schema.props["date_start"].type, j.data.types.Integer)
        and schema.props["date_start"].type.default == 0
    )
    del schema.props["date_start"].type
    assert schema.props["date_start"].__dict__ == {
        "defaultvalue": "0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "date_start",
    }
    assert "description" in schema.props
    assert (
        isinstance(schema.props["description"].type, j.data.types.String)
        and schema.props["description"].type.default == "hello world"
    )
    del schema.props["description"].type
    assert schema.props["description"].__dict__ == {
        "defaultvalue": "hello world",
        "index": True,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "description",
    }
    assert "description2" in schema.props
    assert "description" in schema.props
    assert (
        isinstance(schema.props["description2"].type, j.data.types.String)
        and schema.props["description2"].type.default == 'creature asd"asd ,xzc'
    )
    del schema.props["description2"].type
    assert schema.props["description2"].__dict__ == {
        "defaultvalue": 'creature asd"asd ,xzc',
        "index": False,
        "index_key": True,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "description2",
    }
    assert "llist4" in schema.props
    assert (
        isinstance(schema.props["llist4"].type, j.data.types.List)
        and isinstance(schema.props["llist4"].type.subtype, j.data.types.Integer)
        and schema.props["llist4"].type.default == [1, 2, 3]
    )
    del schema.props["llist4"].type
    assert schema.props["llist4"].__dict__ == {
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": True,
        "unique": False,
        "comment": "",
        "name": "llist4",
    }
    assert "llist5" in schema.props
    assert (
        isinstance(schema.props["llist5"].type, j.data.types.List)
        and isinstance(schema.props["llist5"].type.subtype, j.data.types.Integer)
        and schema.props["llist5"].type.default == [1, 2, 3]
    )
    del schema.props["llist5"].type
    assert schema.props["llist5"].__dict__ == {
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist5",
    }
    assert "llist6" in schema.props
    assert (
        isinstance(schema.props["llist6"].type, j.data.types.List)
        and isinstance(schema.props["llist6"].type.subtype, j.data.types.Integer)
        and schema.props["llist6"].type.default == [1, 2, 3]
    )
    del schema.props["llist6"].type
    assert schema.props["llist6"].__dict__ == {
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist6",
    }
    assert "U" in schema.props
    assert isinstance(schema.props["U"].type, j.data.types.Float) and schema.props["U"].type.default == 0.0
    del schema.props["U"].type
    assert schema.props["U"].__dict__ == {
        "defaultvalue": "0.0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "U",
    }
    assert "nrdefault" in schema.props
    assert (
        isinstance(schema.props["nrdefault"].type, j.data.types.Integer) and schema.props["nrdefault"].type.default == 0
    )
    del schema.props["nrdefault"].type
    assert schema.props["nrdefault"].__dict__ == {
        "defaultvalue": "0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "nrdefault",
    }
    assert "nrdefault2" in schema.props
    assert (
        isinstance(schema.props["nrdefault2"].type, j.data.types.Integer)
        and schema.props["nrdefault2"].type.default == 0
    )
    del schema.props["nrdefault2"].type
    assert schema.props["nrdefault2"].__dict__ == {
        "defaultvalue": "",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "nrdefault2",
    }
    assert "nrdefault3" in schema.props
    assert (
        isinstance(schema.props["nrdefault3"].type, j.data.types.Integer)
        and schema.props["nrdefault3"].type.default == 0
    )
    del schema.props["nrdefault3"].type
    assert schema.props["nrdefault3"].__dict__ == {
        "defaultvalue": "0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "nrdefault3",
    }
    assert "obj" in schema.props
    assert (
        isinstance(schema.props["obj"].type, j.data.types.JSObject) and schema.props["obj"].type.default == "7mada.test"
    )
    del schema.props["obj"].type
    assert schema.props["obj"].__dict__ == {
        "defaultvalue": "7mada.test",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "obj",
    }
