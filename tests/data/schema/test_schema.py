from jumpscale.god import j


def test_schema():
    definition = """
    @url = despiegk.test
    llist = []
    llist2 = "" (LS) #L means = list, S=String
    llist3     = [1,2,3] (LF)
    &nr    = 4


    obj = (O)!7mada.test
    
    
    date_start = 0 (D)
    
       description* = ""        
    description2 ** = (S)
    llist4*** = [1,2,3] (L)
    llist5 = [1,2,3] (LI)
    llist6 = "1,2,3" (LI)
    U = 0.0
    nrdefault = 0
    nrdefault2 = (I)
    nrdefault3 = 0 (I)
    """
    schema = j.data.schema.parse_schema(definition)
    assert schema.url == "despiegk.test"
    assert schema.system_props == {"url": "despiegk.test"}
    assert "llist" in schema.props
    assert schema.props["llist"].__dict__ == {
        "type": "ls",
        "defaultvalue": "[]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist",
    }
    assert "llist2" in schema.props
    assert schema.props["llist2"].__dict__ == {
        "type": "LS",
        "defaultvalue": "",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "L means = list, S=String",
        "name": "llist2",
    }
    assert "llist3" in schema.props
    assert schema.props["llist3"].__dict__ == {
        "type": "LF",
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist3",
    }
    assert "nr" in schema.props
    assert schema.props["nr"].__dict__ == {
        "type": "i",
        "defaultvalue": "4",
        "index": True,
        "index_key": False,
        "index_text": False,
        "unique": True,
        "comment": "",
        "name": "nr",
    }
    assert "date_start" in schema.props
    assert schema.props["date_start"].__dict__ == {
        "type": "D",
        "defaultvalue": "0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "date_start",
    }
    assert "description" in schema.props
    assert schema.props["description"].__dict__ == {
        "type": "str",
        "defaultvalue": "",
        "index": True,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "description",
    }
    assert "description2" in schema.props
    assert schema.props["description2"].__dict__ == {
        "type": "S",
        "defaultvalue": "",
        "index": False,
        "index_key": True,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "description2",
    }
    assert "llist4" in schema.props
    assert schema.props["llist4"].__dict__ == {
        "type": "L",
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": True,
        "unique": False,
        "comment": "",
        "name": "llist4",
    }
    assert "llist5" in schema.props
    assert schema.props["llist5"].__dict__ == {
        "type": "LI",
        "defaultvalue": "[1,2,3]",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist5",
    }
    assert "llist6" in schema.props
    assert schema.props["llist6"].__dict__ == {
        "type": "LI",
        "defaultvalue": "1,2,3",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "llist6",
    }
    assert "U" in schema.props
    assert schema.props["U"].__dict__ == {
        "type": "float",
        "defaultvalue": "0.0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "U",
    }
    assert "nrdefault" in schema.props
    assert schema.props["nrdefault"].__dict__ == {
        "type": "i",
        "defaultvalue": "0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "nrdefault",
    }
    assert "nrdefault2" in schema.props
    assert schema.props["nrdefault2"].__dict__ == {
        "type": "I",
        "defaultvalue": "",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "nrdefault2",
    }
    assert "nrdefault3" in schema.props
    assert schema.props["nrdefault3"].__dict__ == {
        "type": "I",
        "defaultvalue": "0",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "nrdefault3",
    }
    assert "obj" in schema.props
    assert schema.props["obj"].__dict__ == {
        "type": "O",
        "defaultvalue": "7mada.test",
        "index": False,
        "index_key": False,
        "index_text": False,
        "unique": False,
        "comment": "",
        "name": "obj",
    }
