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

__optional__ = True


def export_module_as():
    from . import tables

    return tables
