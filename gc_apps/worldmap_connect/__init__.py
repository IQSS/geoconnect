"""
import requests

data = { 'geoconnect_token': u'JdPGVSg-test-a9yM8gt74ZpLp'}
url = 'http://107.22.231.227/dataverse/import/'

r = requests.post(url, data=data)
print r.text
print r.status_code

"""