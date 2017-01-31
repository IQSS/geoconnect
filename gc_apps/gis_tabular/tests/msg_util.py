from __future__ import print_function
import sys
def msg(s): print (s)
def dashes(char='-'): msg(40*char)
def msgt(s): dashes(); msg(s); dashes()
def msgn(s): dashes(); msg(s)
def msgx(s): dashes('\/'); msg(s); dashes('\/'); sys.exit(0)

