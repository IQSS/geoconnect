from __future__ import print_function
# Hackish:)

def msg(s): print(s)
def dashes(): msg(40*'-')
def msgd(s): dashes(); msg(s)
def msgt(s): dashes(); msg(s); dashes()
def msgn(m): msg('\n'); msg(m); dashes()
