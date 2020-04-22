
from jumpscale.god import j
from hypothesis import given
from hypothesis.strategies import lists, integers


schema = """
            @url = despiegk.test
            llist = []
            listany = (LO)
            llist2 = "" (LS) #L means = list, S=String
            llist3     = [1,2,3] (LF)
            &nr    = 4
            obj = (O)!hmada.test
            lobjs = (LO) !hamada.test

            date_start = 0 (I)
            description* = "hello world"        
            description2 ** = 'a string' (S)
            llist4*** = [1,2,3] (LI)
            llist5 = [1,2,3] (LI)
            llist6 = [1,2,3] (LI)
            U = 0.0
            nrdefault = 0
            nrdefault2 = (I)
            nrdefault3 = 0 (I)
    """


# @given(schema_url()))
# def test_url_convert()(l):
#     pass



def test001_loading_schema_in_compiler():
    c = j.tools.schemac.get_compiler(schema, "python")
    assert c

    assert c._schema_text
    assert c.lang == "python"
    assert c.generator
    c.parse()  # parse schema now
    assert c._parsed_schema is not None
    # import ipdb; ipdb.set_trace()
    print(c.generate())
    c.lang = "crystal"
    c.parse()
    print(c.generate())
