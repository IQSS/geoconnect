from os.path import join, isfile
from msg_util import *

import pandas as pd


def check_csv(fname):
    print 'ok'


    #df = pd.read_csv(fname, nrows=10, converters={'TRACT': lambda x: 'r'+ str(x).zfill(6)})
    df = pd.read_csv(fname, nrows=1,  dtype={'TRACT': '|S6',})


    msg(df.dtypes)
    msg(list(df.columns.values))
    #msg(df.describe())

    #df.TRACT.astype(str)

    #df['TRACTCE_formatted'] = df['TRACT'].map(lambda x: '"%s"' % str(x).zfill(6))

    #print df['TRACTCE_formatted']
    print df['TRACT']

    df.to_csv('input/ok_there2.csv')
    #for r in df[2:4,0:]:
    #    print r
    #for k, v in df.iloc[:,6].convert_objects(convert_numeric=False).iteritems():
    #    print k,v

if __name__=='__main__':
    check_csv(join('input', 'boston_income.csv'))
