import re
import requests
from django.conf import settings

GEONODE_PREFIX = 'geonode:'

class LayerLink(object):

    def __init__(self, name, link, description=None):
        self.name = name
        self.link = link
        self.description = description

class LayerLinkHelper(object):
    """
    For development/debugging, given a WorldMap layer name, create links
    related to various geonode services including:
        - Listing geoserver attributes for the layer
        - Retrieving the current SLD in XML format
        - Showing the classify service url, etc.
    """

    def __init__(self, layer_name, server_name='http://localhost:8000'):

        assert layer_name is not None, "layer_name cannot be None"

        self.layer_name = layer_name    # geonode:boston_social_disorder
        self.server_name = server_name
        if self.server_name.endswith('/'):
            self.server_name = self.server_name[:-1]

        self.layer_name_no_prefix = None # boston_social_disorder
        self.links_dict = {}
        self.links_list = []

        # Secondary processing involving requests
        self.sld_name = None

        self.format_layer_name()
        self.format_layer_links()

    def format_layer_name(self):
        """
        Make sure the layer name has the GEONODE_PREFIX
            e.g. "geonode:boston_social_disorder"
        Set a variable w/o the prefix
            e.g. layer_name_no_prefix = "boston_social_disorder"
        """
        if not self.layer_name.startswith(GEONODE_PREFIX):
            self.layer_name = '%s%s' % (GEONODE_PREFIX, self.layer_name)

        self.layer_name_no_prefix = self.layer_name[len(GEONODE_PREFIX):]


    def add_link(self, name, link, description=''):
        """
        Add a LayerLink object to "links_list"
        """
        layer_link_obj = LayerLink(name, link, description)

        # add to list
        self.links_list.append(layer_link_obj)

        # add to dict
        self.links_dict[name] = layer_link_obj

        print('links count: %s' % len(self.links_list))

    def get_geoserver(self):

        return self.server_name.replace(':8000', ':8080')


    def format_layer_links(self):

        # View layer
        view_url = '%s/data/%s' % (self.server_name, self.layer_name)
        self.add_link('wm_layer', view_url, 'WorldMap layer view')

        # Geoserver attributes
        attr_url = ('%s/geoserver/rest/sldservice/%s/attributes.xml'\
            % (self.get_geoserver(), self.layer_name))
        self.add_link('attributes', attr_url, 'Geoserver Attributes')

        # SLD Name
        layer_url = '%s/geoserver/rest/layers/%s.html' %\
            (self.get_geoserver(), self.layer_name_no_prefix)
        self.add_link('sld_name', layer_url, 'SLD name')

        if not self.get_sld_name():
            return

        sld_url = '%s/geoserver/rest/styles/%s.sld' %\
            (self.get_geoserver(), self.sld_name)
        self.add_link('sld_xml', sld_url, 'current SLD XML')

        sld_url2 = '%s/geoserver/web/?wicket:bookmarkablePage=:org.geoserver.wms.web.data.StyleEditPage&name=%s' %\
            (self.get_geoserver(), self.sld_name)
        self.add_link('sld_xml2', sld_url2, 'Editable/Formatted SLD XML')


    def get_sld_name(self):
        """
        Retrieve the layer's SLD name from the server
        """
        if not 'sld_name' in self.links_dict:
            return False

        sld_url = self.links_dict['sld_name'].link

        print ('Attempt to retrieve SLD'
                'sld_url: %s' % sld_url)

        r = requests.get(sld_url, auth=settings.WORLDMAP_ACCOUNT_AUTH)

        print r.status_code
        if not r.status_code == 200:
            print 'Failed to retrieve SLD'
            return False

        # Parse out the SLD Name
        sld_search = re.search(r'<li>Default style: StyleInfoImpl\[(.*)\]',\
                        r.text, re.IGNORECASE)

        if sld_search is None:
            print 'Failed to retrieve SLD'
            return False

        sld_name = sld_search.group(1)

        self.sld_name = sld_name
        return True
        """
        if title_search:
            title = title_search.group(1)

        content = r.text
        start_tag =
        idx = content.find('<li>Default style: StyleInfoImpl[')
        if idx == -1:
            print 'Failed to retrieve SLD'
            return

        end_idx = content.find(']', idx +

        print r.text
        """
