import terminaltables as tt

TABLE_TYPES = {'ascii': tt.AsciiTable, 'single': tt.SingleTable, 'double': tt.DoubleTable}

def create(title, data, type_='ascii'):

    table_type = TABLE_TYPES.get(type_)
    if not table_type:
        raise ValueError("invalid type {} allowed types are {}".format(table_type, TABLE_TYPES.keys()))

    table = table_type(data, title)

    return table.table

