"""Dictionary of WorldMap download type links with labels for users"""
from collections import OrderedDict

DOWNLOAD_TYPE_LABEL_LOOKUP = dict(KML='label',
                            csv='KML (Keyhole Markup Language)',
                            gml='GML (Geography Markup Language)',
                            jpg='JPG (image)',
                            json='JSON',
                            pdf='PDF',
                            png='PNG (image)',
                            tiff='TIFF (image)',
                            xls='Excel (.xls)',
                            zip='Shapefile (.zip)')



class DownloadLinkFormatter(object):

    def __init__(self, links_dict):
        assert type(links_dict) in (dict, OrderedDict), 'links_dict must be a dict or OrderedDict'

        self.links_dict = links_dict # { 'zip' : 'http:/some-url ', 'pdf' : 'http:/some-other-url '}
        self.formatted_links = None

    def get_formatted_links(self):
        self.formatted_links = []

        for key, url in self.links_dict.items():
            single_link = dict(link_type=key,
                            url=url,
                            label=DownloadLinkFormatter.get_download_type_label(key)
                            )
            self.formatted_links.append(single_link)
        return formatted_links

    @staticmethod
    def get_download_type_label(dtype):
        """Given a download type (jpg, json, pdf, etc), return the appropriate label"""

        label = DOWNLOAD_TYPE_LABEL_LOOKUP.get(dtype, None)
        assert label is not None, "dtype not found: %s" % dtype

        return label
