from django.template.defaultfilters import slugify
from string import digits


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

def get_pandas_numeric_dtypes():
    """helpful list when working with pandas"""

    return ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

def is_pandas_dtype_numeric(dtype):
    """Check if a given dtype is numeric"""

    if dtype in get_pandas_numeric_dtypes():
        return True

def normalize_colname(colname, position):
    """
    Return a string that complies with the characters PostgreSQL allows as column names.
    Django's "slugify" does most of the work but we replace hyphens with underscores
    and strip leading digits. If the resulting string is empty, return a robotic but safe
    string based on the position of the column in the source data (i.e. "column_007").
    """
    # The string returned must be a valid column name in PostgreSQL.
    # From https://www.postgresql.org/docs/9.6/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    # "SQL identifiers and key words must begin with a letter (a-z, but also letters with diacritical marks and non-Latin letters) or an underscore (_). Subsequent characters in an identifier or key word can be letters, underscores, digits (0-9), or dollar signs ($). Note that dollar signs are not allowed in identifiers according to the letter of the SQL standard, so their use might render applications less portable. The SQL standard will not define a key word that contains digits or starts or ends with an underscore, so identifiers of this form are safe against possible conflict with future extensions of the standard."
    normalized = slugify(colname).replace('-', '_').lstrip(digits)
    if (normalized == ''):
        # 7 becomes 007
        return 'column_' + '%03d' % position
    return normalized
