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

    def has_token_expired(self, current_time=None):
        """Check if the token has expired.
        Find the difference between the current time and the token's "last_refresh_time"
        Compare it to the ApplicationInfo "time_limit_seconds" attribute

        :param current_time: datetime object that is timezone aware or None
		:returns True/False
        """
        if current_time is None:
            current_time = datetime.utcnow().replace(tzinfo=utc)

        try:
            mod_time = current_time - self.last_refresh_time
        except:
            return True

        if mod_time.seconds > self.application.time_limit_seconds:
            self.has_expired = True
            self.save()
            return True

        return False

    def refresh_token(self):
		"""Refresh the token.  Called each time the API is used"""

        current_time = datetime.utcnow().replace(tzinfo=utc)
        if self.has_token_expired(current_time):
            return False            
        self.last_refresh_time = current_time
        self.save()
        return True

    def save(self, *args, **kwargs):
        """On save, generate a unique token using sha224"

		if not self.id:
            super(DataverseToken, self).save(*args, **kwargs)
		
        if not self.token:
            self.token = sha224('[id:%s][sf:%s]' % (self.id, self.single_file.md5)).hexdigest()

        super(DataverseToken, self).save(*args, **kwargs)

    def get_mapit_link_with_token(self, request):
        #metadata_url = reverse('view_single_file_metadata', kwargs={'dv_token' : self.token})

        d = {}
        metadata_url = reverse('view_single_file_metadata_base_url', kwargs={})
        d['cb'] = request.build_absolute_uri(metadata_url) #request.get_host()
        callback_url = urllib.urlencode(d)
        return self.application.mapit_link + '%s/?%s' % (self.token, callback_url)

```
