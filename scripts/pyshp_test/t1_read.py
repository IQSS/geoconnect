import shapefile
import timeit
import json
import sys
def msg(s): print s
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()

class ShapefileInfoReader:
    def __init__(self, fname):
        self.sf = shapefile.Reader(fname)  # basename

    def show(self):
        shapes = self.sf.shapes()

        msg('bounding box: %s' % self.sf.bbox)
        msg('bounding box: %s' % self.sf.bbox)
        
        for f in self.sf.fields:
            print f
                        
        #print self.sf.fields       
        print json.dumps(self.sf.fields)
        for rec in self.sf.records():
            print rec
    
def shp_read_test():
    
    #f1 = '/Users/rmp553/Google Drive/Dataverse/BARI/test_data/social_disorder_in_boston/social_disorder_in_boston_yqh'
    #f1 = '../worldmap_api/test_shps/social_disorder_in_boston/social_disorder_in_boston_yqh'
    f1 = '../worldmap_api/test_shps/income_in_boston_gui/income_in_boston_gui'

    sf = shapefile.Reader(f1 + '.shp')
    print sf.records()
    sys.exit(0)


    shp_info = ShapefileInfoReader(f1)
    shp_info.show()
    dashes()
if __name__=='__main__':
    #f1 = '/Users/rmp553/Google Drive/Dataverse/BARI/test_data/social_disorder_in_boston/social_disorder_in_boston_yqh'
    
    print(timeit.timeit("shp_read_test()", setup="from __main__ import shp_read_test", number=1))
