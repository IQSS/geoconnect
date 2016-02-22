import pandas as pd

t1 = 'test_dv_files/2-ca-measures.tab'
t2 = 'test_dv_files/boston_income.tab'

"""
for l in open(t2, 'rb').readlines():
    print l.split('\t')
    print '-' * 40
"""

df = pd.read_csv(t2, sep='\t')
print df.columns

# Add zero padded column
#
df['TRACT-formatted']=  df['TRACT'].apply(lambda x: '{0:0>6}'.format(x))

df.to_csv('fname', '\t')
