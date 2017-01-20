"""Format the dictionary of WorldMap download type links with labels for users"""

from collections import OrderedDict
import json

LABEL_UNKOWN = 'UNKNOWN LABEL'

DOWNLOAD_TYPE_LABEL_LOOKUP = dict(KML='KML (Keyhole Markup Language)',
                            csv='CSV (Comma-Separated Values)',
                            gml='GML (Geography Markup Language)',
                            jpg='JPG (Joint Photographic Experts Group)',
                            json='JSON (JavaScript Object Notation)',
                            pdf='PDF (Portable Document Format)',
                            png='PNG (Portable Network Graphics)',
                            tiff='TIFF (Tagged Image File Format)',
                            xls='XLS (Microsoft Excel)',
                            zip='ZIP (ZIP Compressed Shapefile)')



class DownloadLinkFormatter(object):

    def __init__(self, links_dict):
        assert type(links_dict) in (dict, OrderedDict), 'links_dict must be a dict or OrderedDict'

        self.links_dict = links_dict # { 'zip' : 'http:/some-url ', 'pdf' : 'http:/some-other-url '}

    def get_formatted_links(self):
        formatted_links = []

        for key, url in self.links_dict.items():
            single_link = dict(link_type=key,
                            url=url,
                            label=DownloadLinkFormatter.get_download_type_label(key)
                            )
            formatted_links.append(single_link)

        return formatted_links
        return json.dumps(formatted_links)

    @staticmethod
    def get_download_type_label(dtype):
        """Given a download type (jpg, json, pdf, etc), return the appropriate label"""

        label = DOWNLOAD_TYPE_LABEL_LOOKUP.get(dtype, None)
        if label is None:
            label = '%s (%s)' % (dype, LABEL_UNKOWN)

        return label

"""
Example input:

{
    "json": "http://worldmap.harvard.edu/download/wfs/33057/json?outputFormat=json&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aj_election_pr_election_pr&version=1.0.0",
    "csv": "http://worldmap.harvard.edu/download/wfs/33057/csv?outputFormat=csv&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aj_election_pr_election_pr&version=1.0.0",
    "png": "http://worldmap.harvard.edu/download/wms/33057/png?layers=geonode%3Aj_election_pr_election_pr&width=503&bbox=-71.0858752417%2C42.2989477917%2C-70.9990388296%2C42.3938100655&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550",
    "zip": "http://worldmap.harvard.edu/download/wfs/33057/zip?outputFormat=SHAPE-ZIP&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aj_election_pr_election_pr&version=1.0.0",
    "gml": "http://worldmap.harvard.edu/download/wfs/33057/gml?outputFormat=text%2Fxml%3B+subtype%3Dgml%2F3.1.1&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aj_election_pr_election_pr&version=1.0.0",
    "tiff": "http://worldmap.harvard.edu/download/wms/33057/tiff?layers=geonode%3Aj_election_pr_election_pr&width=503&bbox=-71.0858752417%2C42.2989477917%2C-70.9990388296%2C42.3938100655&service=WMS&format=image%2Fgeotiff&srs=EPSG%3A4326&request=GetMap&height=550",
    "KML": "http://worldmap.harvard.edu/download/wms_kml/33057/kml?layers=geonode%3Aj_election_pr_election_pr&mode=refresh",
    "xls": "http://worldmap.harvard.edu/download/wfs/33057/xls?outputFormat=excel&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aj_election_pr_election_pr&version=1.0.0",
    "pdf": "http://worldmap.harvard.edu/download/wms/33057/pdf?layers=geonode%3Aj_election_pr_election_pr&width=503&bbox=-71.0858752417%2C42.2989477917%2C-70.9990388296%2C42.3938100655&service=WMS&format=application%2Fpdf&srs=EPSG%3A4326&request=GetMap&height=550",
    "jpg": "http://worldmap.harvard.edu/download/wms/33057/jpg?layers=geonode%3Aj_election_pr_election_pr&width=503&bbox=-71.0858752417%2C42.2989477917%2C-70.9990388296%2C42.3938100655&service=WMS&format=image%2Fjpeg&srs=EPSG%3A4326&request=GetMap&height=550"
}

"""
