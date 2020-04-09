"""This module helps around creation of terminal tables

JS-NG> j.data.terminaltable.print_table("users", [ ["id", "name"], ["1", "ahmed"], ["2", "xmonader"]])           
+users----------+
| id | name     |
+----+----------+
| 1  | ahmed    |
| 2  | xmonader |
+----+----------+

JS-NG> tbl = j.data.terminaltable.create("users", [ ["id", "name"], ["1", "ahmed"], ["2", "xmonader"]])          
JS-NG> print(tbl)                                                                                                
+users----------+
| id | name     |
+----+----------+
| 1  | ahmed    |
| 2  | xmonader |
+----+----------+
"""
import terminaltables as tt

TABLE_TYPES = {"ascii": tt.AsciiTable, "single": tt.SingleTable, "double": tt.DoubleTable}


def create(title, data, type_="ascii"):

    table_type = TABLE_TYPES.get(type_)
    if not table_type:
        raise ValueError("invalid type {} allowed types are {}".format(table_type, TABLE_TYPES.keys()))

    table = table_type(data, title)

    return table.table


def print_table(title, data, type_="ascii"):
    print(create(title, data, type_))
