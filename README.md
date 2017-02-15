## _Note: These instructions need updating and should not be used if setting up a Dataverse installation_

## geoconnect

GeoConnect works as a middle layer, allowing [Dataverse](http://datascience.iq.harvard.edu/dataverse) files to be visualized on the [Harvard WorldMap](http://worldmap.harvard.edu/).

###

[Boston Area Research Initiative](http://www.bostonarearesearchinitiative.net/) project to connect the [Dataverse](http://datascience.iq.harvard.edu/dataverse) to the [Worldmap](http://worldmap.harvard.edu/).  

### Use Cases

* Add a GIS dataset to the Dataverse and visualize it on the WorldMap
* From the WorldMap, search for Dataverse datasets in a given geographic area for a specific time period




![geoconnect screenshot](geoconnect/static/images/screenshot_inspect_shapefile.png?raw=true "Inspect Shapefile")

### Local Installation Instructions

#### Install [pip](http://pip.readthedocs.org/en/latest/installing.html)

* use sudo if needed
* if on Windows, make sure [python](https://www.python.org/downloads/) is installed.

#### Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)

* depends on pip
* if on windows, either install [virtualenvwrapper-win-1.1.5](https://pypi.python.org/pypi/virtualenvwrapper-win) or [cygwin](https://www.cygwin.com/).
* remember to set the (shell startup file)[http://virtualenvwrapper.readthedocs.org/en/latest/install.html#shell-startup-file]
```
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh
```
or, on windows, [this](http://stackoverflow.com/questions/2615968/installing-virtualenvwrapper-on-windows) might be helpful.

#### Pull down the [geoconnect repository](https://github.com/IQSS/geoconnect)

* Use the [mac client](https://mac.github.com/) if desired or [windows client](https://windows.github.com/)

### Setup on the local machine

#### cd into the geoconnect repository

```
cd ~\geoconnect
```

#### Install the virtualenv and the requirements

This may take a minute or two.  Xcode needs to be installed.

```
mkvirtualenv geoconnect
pip install -r requirements/local.txt
```

If you run into Xcode (or other errors) when running the install, google it.  Sometimes the [Xcode license agreement hasn't been accepted](http://stackoverflow.com/questions/26197347/agreeing-to-the-xcode-ios-license-requires-admin-privileges-please-re-run-as-r/26197363#26197363)

#### Configure settings (still in ~\geoconnect)

* Edit the [postactivate script for the virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/scripts.html#postactivate).

```
vim $VIRTUAL_ENV/bin/postactivate
```
On windows:
```
vim %VIRTUAL_ENV%\Scripts\activate.bat
```

'vim' may be any text editor

* add these lines to the postactivate file and save the file

```
export DJANGO_DEBUG=True
export DJANGO_SETTINGS_MODULE=geoconnect.settings.local
```
On windows:
```
set "DJANGO_DEBUG=True"
set "DJANGO_SETTINGS_MODULE=geoconnect.settings.local"
```

* Test the 'postactivate' script from the command line

```
deactivate
workon geoconnect
echo $DJANGO_SETTINGS_MODULE
```
On Windows, use:
```
echo %DJANGO_SETTINGS_MODULE%
```

You should see ```geoconnect.settings.local```

#### Create/sync the database (still in ~\geoconnect)



```
#Create/sync the database (still in ~\geoconnect)
python manage.py migrate    # step 1 for a new database
python manage.py migrate --run-syncdb  # step 2 for a new database

#python manage.py  migrate --fake-initial # if the tables already exist
```

- Add initial database

```
python manage.py loaddata --app registered_dataverse incoming_filetypes_initial_data.json
python manage.py loaddata --app layer_classification initial_data.json
```
  - To run on a localhost, add this data: ```python manage.py loaddata --app registered_dataverse registered_dv_localhost.json```

- Create a superuser

```
python manage.py createsuperuser
```

#### Run the test server (still in ~\geoconnect\geoconnect)

```
python manage.py runserver 8070
```

1. Check if the server is up: http://127.0.0.1:8070
1. Check if the admin page is available: http://127.0.0.1:8070/geo-connect-admin/
- if (1) and (2), feel grateful to be alive

### Re-run the test server

```
cd ~/geoconnect/ # example: cd /Users/mheppler/iqss-github/geoconnect
workon geoconnect
atom .  # to open in ATOM
python manage.py runserver 8070
```

## Dataverse settings

Dataverse needs these settings to work on mapping.

### Dataverse config settings

```sql
INSERT into setting VALUES (':GeoconnectCreateEditMaps', 'true');
INSERT into setting VALUES (':GeoconnectViewMaps', 'true');
```

### Dataverse setting for the 'mapitlink'

- If ```GEOCONNECT``` entry doesn't exist, use:

```sql
INSERT INTO worldmapauth_tokentype (contactemail, hostname, ipaddress, mapitlink, name, timelimitminutes, timelimitseconds, md5, created, modified)
VALUES ('support@dataverse.org', '127.0.0.1:8070', '127.0.0.1:8070', 'http://127.0.0.1:8070/shapefile/map-it', 'GEOCONNECT', 30, 1800, '38c0a931b2d582a5c43fc79405b30c22', NOW(), NOW())
```

- If ```GEOCONNECT``` entry already exists, use:

```sql
UPDATE worldmapauth_tokentype SET mapitlink = 'http://127.0.0.1:8070/shapefile/map-it' WHERE name = 'GEOCONNECT';
```
