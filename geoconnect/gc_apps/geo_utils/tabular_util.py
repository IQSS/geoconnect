from django.template.defaultfilters import slugify


FORMATTED_COLUMN_EXTENSION = '_formatted'

def get_formatted_column_name(colname):
    """When adding a new column to a tabular file, add a suffix to the end"""
    assert colname is not None, "colname cannot be None"

    return '%s%s' % (colname, FORMATTED_COLUMN_EXTENSION)


def get_orig_column_name(colname):
    """Retrieve the original column name by removing the suffix"""
    assert colname is not None, "colname cannot be None"
    assert colname.endswith(FORMATTED_COLUMN_EXTENSION),\
        'colname must end with %s' % FORMATTED_COLUMN_EXTENSION

    split_str = colname.rsplit(FORMATTED_COLUMN_EXTENSION, 1)

    return ''.join(split_str)

def get_worldmap_colname_format(colname):
    """Format the column in the same method as Worldmap"""
    assert colname is not None, "colname cannot be None"

    return slugify(unicode(colname)).replace('-', '_')

def get_pandas_numeric_dtypes():
    """helpful list when working with pandas"""

    return ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

def is_pandas_dtype_numeric(dtype):
    """Check if a given dtype is numeric"""

    if dtype in get_pandas_numeric_dtypes():
        return True
