"""
Way to reproduce the uploading of shapefiles used for target layers
"""
import sys
from os.path import dirname, realpath, isdir, isfile, join

from abstract_data import abstract_info_list



class AbstractHelp(object):

    def __init__(self, title, year, dataset_doi, desc_filename):
        self.title = title
        self.year = year
        self.dataset_doi = dataset_doi
        self.desc_filename = desc_filename

    def get_description(self):

        desc = """
=================================
## Title
=================================
{2} (BARI)

=================================
## Description
=================================
{0}
<br /><br />Provided by the Boston Area Research Initiative (BARI): <a href="https://www.northeastern.edu/csshresearch/bostonarearesearchinitiative/">https://www.northeastern.edu/csshresearch/bostonarearesearchinitiative/</a>
<br /><br />This file, along with other administrative geographies utilized by the City of Boston, may be found in the <a href="{1}">Dataverse repository</a>:
<br /><br />
<ul>
<li>Data: <a href="{1}">{1}</a></li>
<li>Documentation: <a href="http://dx.doi.org/10.7910/DVN/C5IULB">http://dx.doi.org/10.7910/DVN/C5IULB</a></li>
</ul>""".format(self.get_description_from_file(), self.dataset_doi, self.title)

        return desc


    def get_description_from_file(self):
        CURRENT_DIR = dirname(realpath(__file__))
        DESC_DIRECTORY = join(CURRENT_DIR , 'descriptions')
        if not isdir(DESC_DIRECTORY):
            print 'Directory does not exist', DESC_DIRECTORY
            sys.exit(0)

        desc_file = join(DESC_DIRECTORY, self.desc_filename)
        if not isfile(desc_file):
            print 'Description file not found', desc_file
            sys.exit(0)

        return open(desc_file, 'r').read()


def show_abstracts(info_list):
    print '\n' + ('-' * 30)
    print 'Please choose one:\n'
    for idx, info in enumerate(info_list):
        ab_help = AbstractHelp(*info)
        print '(%d) %s' % (idx+1, ab_help.title)
    print '\n' + ('-' * 30)


def format_selected_abstract(selected_idx, info_list):
    assert selected_idx.isdigit(), "selected_idx must be a digit.  Not: %s" % selected_idx

    for idx, info in enumerate(info_list):
        if (idx+1) == int(selected_idx):
            ab_help = AbstractHelp(*info)
            print ab_help.get_description()
            return
    print 'Sorry! [%s] not found! Please select a number from the list: ' % selected_idx
    show_abstracts(info_list)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        format_selected_abstract(sys.argv[1], abstract_info_list)
    else:
        show_abstracts(abstract_info_list)
