## Dataverse Session Token

The idea of a dataverse session token is that a GeoConnect user may have access to a particular Dataverse Dataset for a limited time period.
A use case is a user trying to data an Excel file, which would involve the following process
	+ In Dataverse: User has specified that an uploaded Excel data has GIS data
	+ Dataverse presents user with a "Map It" button  
	+ Clicking "Map It" generates a token used by GeoConnect
		+ Token specifies API access for a specific file and user (e.g. only a user with edit permissions can update the DV metadata)
	+ User taken to GeoConnect where asked to specify lat, long columns 
	+ GeoConnect creates shapefile which is sent to the WorldMap
	+ WorldMap metadata sent back to Dataverse
	+ User can go back to Dataverse or go to the WorldMap

### Tables to support the Dataverse Session Token

Conceptually/Informally the support for database tokens may resemble:

- Authorized Applications
	1. IP Address	
	1. Hostname
	1. Application key
	1. Time Limit (seconds)
	1. Max Existence (seconds)	# How long token may exist from create time
	
- GeoConnect Token Table
	1. token
	1. authorized application (FK)
	1. create time
	1. refresh time
	1. dataset id
	1. DVN user id
	1. may_update_metadata 
		- (Based on user permissions. example, True if the person is the dataset owner or an editor?)

```python

# From some working proof of concept code 

class ApplicationInfo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(help_text='contact info, etc')
    contact_email = models.EmailField()
    
    hostname = models.CharField(max_length=255, blank=True)
    ip_address = models.CharField(max_length=15, blank=True)
    
    mapit_link = models.URLField(help_text='http://geoconnect.harvard.edu')	# append token to this link
    #api_permissions = models.ManyToManyField(APIPermission, blank=True, null=True)
    
    time_limit_minutes = models.IntegerField(default=30, help_text='in minutes')
    time_limit_seconds = models.IntegerField(default=0, help_text='autofilled on save')
    
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
    
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)


class DataverseToken(models.Model):
    """Example of a "mock token"
    """
    token = models.CharField(max_length=255, blank=True, help_text = 'auto-filled on save', db_index=True)
    application = models.ForeignKey(ApplicationInfo)

    dataverse_user = models.ForeignKey(User)
    single_file = models.ForeignKey(SingleFile)
    
    has_expired = models.BooleanField(default=False)
    #dataset_version = models.IntegerField()
    
    last_refresh_time =  models.DateTimeField(auto_now_add=True)
           
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s (%s)' % (self.dataverse_user, self.single_file)

```
