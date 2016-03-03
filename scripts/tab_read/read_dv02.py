import pandas as pd
import csvkit
from csvkit import sql as csvkit_sql
from csvkit import table
from csv import QUOTE_NONNUMERIC, QUOTE_NONE, QUOTE_MINIMAL

def msg(m): print m
def dashes(): print '-' *40
def msgt(m): dashes(); msg(m); dashes()

t3 = 'test_dv_files/CBG Annual and Longitudinal Measures.tab'
t1 = 'test_dv_files/2-ca-measures.tab'
t2 = 'test_dv_files/boston_income.tab'

t4_out = 'test_dv_files/out_file.tab'

def pandas_format():
    # --------------------------------------
    msgt('(1) pandas open, make formatted column')
    # --------------------------------------
    df = pd.read_csv(t3, sep='\t')
    print df['BG_ID_10'][:5]
    df['format_col'] = df['BG_ID_10'].apply(\
                       lambda x: "{0}".format(x))
    #                    lambda x: '""{0}""'.format(x))
    print df['format_col'][:5], len(df['format_col'][:5][1])
    msgt('Columns in dataframe')
    print df.columns

    print df[:3].to_sql('mytable', )
    return

    df[:3].to_csv(t4_out,\
            sep='\t',\
            index=False,\
            quoting=QUOTE_NONNUMERIC)

    print 'file written', t4_out

def csv_to_table():
    # --------------------------------------
    msgt('(2) csvkit to table')
    # --------------------------------------
    fh = open(t4_out, 'rb')
    csv_args = dict(delimiter='\t',\
                    quotechar='"')
    print 'QUOTE_NONE', QUOTE_NONE
    csv_table = table.Table.from_csv(f=fh,\
                            name='tname',\
                            snifflimit=None,\
                            #quoting=QUOTE_NONNUMERIC,\
        #                    **csv_args\
                            )
    for col in csv_table:
        msg('%s, %s' % (col.name, col.type))

    sql_table = csvkit_sql.make_table(csv_table, 'new_table')
    create_table_sql = csvkit_sql.make_create_table_statement(sql_table, dialect="postgresql")
    msg('create_table_sql: %s' % create_table_sql)
    msg(csv_table.to_rows())

def csv_to_table2():
    # --------------------------------------
    msgt('(3) csvkit to table reformat')
    # --------------------------------------
    fh = open(t4_out, 'rb')
    csv_args = dict(delimiter='\t',\
                    quotechar='"')
    csv_table = table.Table.from_csv(f=fh,\
                            name='tname',\
                            snifflimit=None,\
                            )
    print [c.name for c in csv_table]


    last_col = csv_table[-1]
    last_col.type = unicode

    for idx, val in enumerate(last_col):
        last_col[idx] = '%s' % val
    #last_col = ['%s' % x for x in last_col]
    #print last_col[0]

    msg(csv_table.to_rows())

    print [ '%s, %s' % (c.name, c.type) for c in csv_table]

    return

    print 'last_col', last_col.order
    col_num = len(csv_table)
    print 'col_num', col_num

    quoted_data = [u'"%s"' % val for val in last_col]
    print 'quoted_data', quoted_data
    #return

    new_column = table.Column(order=last_col.order,\
                            name=last_col.name,\
                            l=quoted_data,\
                            #normal_type=None,\
                            )
                            #normal_type=None)

    csv_table.pop(-1)



    csv_table.append(new_column)

    sql_table = csvkit_sql.make_table(csv_table, 'new_table')
    create_table_sql = csvkit_sql.make_create_table_statement(sql_table, dialect="postgresql")
    msg('create_table_sql: %s' % create_table_sql)

    msg(csv_table.to_rows())

    return
    msgt('new_column')
    msg(new_column)
    print new_column.name
    for val in new_column: print val
    #print len(new_column)

    """
    print csv_table.columns
    for col in csv_table:
        msg('%s, %s' % (col.name, col.type))

    sql_table = csvkit_sql.make_table(csv_table, 'new_table')
    create_table_sql = csvkit_sql.make_create_table_statement(sql_table, dialect="postgresql")
    msg('create_table_sql: %s' % create_table_sql)
    msg(csv_table.to_rows())
    """
def try_detect_disable():

    pandas_format()
    #csv_to_table()
    #csv_to_table2()

if __name__ == '__main__':
    try_detect_disable()

#df = pd.read_csv(t2, sep='\t')
#print df.columns

# Add zero padded column
#
#df['TRACT-formatted']=  df['TRACT'].apply(lambda x: '{0:0>6}'.format(x))

#df.to_csv('fname', '\t')

# Format Attempts
"""
nope (1) single quote in front
(2) double quotes
(3) double quotes disable sniffer
"""
