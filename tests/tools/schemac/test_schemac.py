
from jumpscale.god import j
from hypothesis import given
from hypothesis.strategies import lists, integers


schema = """
            @url = despiegk.test
            listany = (LO)
            llist2 = "" (LS) #L means = list, S=String
            llist3     = [1,2,3] (LF)
            status = "on,off" (E) 
            happy = "yes, no" (E)
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


valid_generated_python= """
#GENERATED CLASS DONT EDIT
from jumpscale.core.base import Base, fields


class DespiegkTest(Base):
    listany = fields.List(fields.Object())
    llist2 = fields.List(fields.String())
    llist3 = fields.List(fields.Float())
    nr = fields.String(default="4")
    obj = fields.Object()
    lobjs = fields.List(fields.Object())
    date_start = fields.Integer(default=0)
    description = fields.String(default="hello world")
    description2 = fields.String(default="a string")
    llist4 = fields.List(fields.Integer())
    llist5 = fields.List(fields.Integer())
    llist6 = fields.List(fields.Integer())
    U = fields.String(default="0.0")
    nrdefault = fields.String(default="0")
    nrdefault2 = fields.Integer()
    nrdefault3 = fields.Integer(default=0)

"""

valid_generated_crystal = """
class DespiegkTest
    property listany : [] of Object
    property llist2 : [] of String
    property llist3 : [] of Float
    property nr = "4"
    property obj : HmadaTest
    property lobjs : [] of HamadaTest
    property date_start = 0
    property description = "hello world"
    property description2 = "a string"
    property llist4 : [] of Int64
    property llist5 : [] of Int64
    property llist6 : [] of Int64
    property U = "0.0"
    property nrdefault = "0"
    property nrdefault2 : Int64
    property nrdefault3 = 0

end 
"""


def test001_loading_schema_in_compiler():
    c = j.tools.schemac.get_compiler(schema, "python")
    assert c

    assert c._schema_text
    assert c.lang == "python"
    assert c.generator
    c.parse()  # parse schema now
    assert c._parsed_schema is not None
    generated_python =c.generate()
    print(generated_python)

    for line in valid_generated_python.splitlines():
        if line.strip():
            assert line in generated_python

    c.lang = "crystal"
    c.parse()
    generated_crystal = c.generate()
    print(generated_crystal)
    for line in valid_generated_crystal.splitlines():
        if line.strip():
            assert line in generated_crystal