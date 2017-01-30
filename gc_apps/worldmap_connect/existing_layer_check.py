


class ExistingLayerRetriever(object):
    def __init__(self):
        pass



"""
import requests, json
url = 'http://127.0.0.1:8000/dataverse/api/layer-info/'
auth = ('rp', '123')
#data = {"dataverse_installation_name":"https://RAD-rprasad.harvard.edu", "datafile_id":1227}
data = {"dataverse_installation_name":"http://localhost:8000", "datafile_id":67193}
#data = {"dataverse_installation_name":"http://localhost:8000", "datafile_id":15562}
r = requests.post(url, auth=auth, data=data)
d =r.json()
print json.dumps(d, indent=4)


url = 'http://127.0.0.1:8000/datatables/api/join/36'
auth = ('rp', '123')
data = {"dataverse_installation_name":"https://RAD-rprasad.harvard.edu", "datafile_id":1227}
data = {"dataverse_installation_name":"http://localhost:8000", "datafile_id":67193}

r = requests.post(url, auth=auth, data=data)
d =r.json()
print json.dumps(d, indent=4)


"""
