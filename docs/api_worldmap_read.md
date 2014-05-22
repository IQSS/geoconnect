# Dataverse user info
dv_user_id = models.IntegerField()          # for API calls
dv_username = models.CharField(max_length=255)  # for display

# Owning dataverse
dv_id = models.IntegerField()       # for API calls.  dvobject.id; dtype='Dataverse'
dv_name = models.CharField(max_length=255)  # for display

# Dataset Info
dataset_id = models.IntegerField()  # for API calls.  dvobject.id; dtype='Dataset'
dataset_name = models.CharField(max_length=255)  # for display
dataset_citation = models.TextField(blank=True) # for display

# DataFile
datafile_id = models.IntegerField()  # for API calls.  dvobject.id; dtype='DataFile'
datafile_version = models.BigIntegerField(blank=True, null=True)
datafile_name = models.CharField(max_length=255)    # for display; filemetadata.label   (dvobject.id = filemetadata.datafile_id)
datafile_desc = models.TextField(blank=True)    # for display; filemetadata.description   (dvobject.id = filemetadata.datafile_id)
datafile_type = models.CharField(max_length=255)    # dvobject.contenttype
datafile_expected_md5_checksum = models.CharField(blank=True, max_length=255)    # dvobject.md5

# session token
# Token used to make requests of the Dataverse api; may expire, be refreshed
dv_session_token = models.CharField(max_length=255, blank=True)
