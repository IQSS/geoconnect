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
class DataverseToken(models.Model):
    """Superclass for a GIS File "Helper"
    - Examples of GIS files: shapefiles, GeoTiffs, spreadsheets or delimited text files with lat/lng, GeoJSON etc
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
`