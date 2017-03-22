# Local Installation Instructions

GeoConnect works as a middle layer, allowing [Dataverse](http://datascience.iq.harvard.edu/dataverse) files to be visualized on the [Harvard WorldMap](http://worldmap.harvard.edu/).

*caveat*: Directions not too windows friendly...

## Prerequisites

Note: use python 2.7+.  Not yet upgraded for 3.5+

### Install [pip](http://pip.readthedocs.org/en/latest/installing.html)

* use sudo if needed  (mac users, use sudo)
* if on Windows, make sure [python](https://www.python.org/downloads/) is installed.

### Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/install.html#basic-installation)

* The virtualenvwrapper may be installed via pip:

    ```
    pip install virtualenvwrapper
    ```

  * On windows, either install [virtualenvwrapper-win-1.1.5](https://pypi.python.org/pypi/virtualenvwrapper-win) or [cygwin](https://www.cygwin.com/).

* Set the shell/Terminal to use virtualenvwrapper.
  - For Mac users:
    1. Open a new terminal
    2. Open your ```.bash_profile``` for editing
    3. Add these lines

        ```
        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/Devel
        source /usr/local/bin/virtualenvwrapper.sh
        ```

    4. Reference: http://virtualenvwrapper.readthedocs.org/en/latest/install.html#shell-startup-file
  - If you're using windows, [this](http://stackoverflow.com/questions/2615968/installing-virtualenvwrapper-on-windows) might be helpful.

### Install [Github Desktop](https://desktop.github.com/)

- Or, if you choose, use the command line to access github

### Install [ATOM editor](https://atom.io/) (recommended)

- This is Github's text editor

## Local Setup

### Get the repository

- Use Github Desktop to pull down the [geoconnect repository](https://github.com/IQSS/geoconnect)
- Alternately, use the command line:
```
git clone git@github.com:IQSS/geoconnect.git
```

### Make a virtualenv and install requirements

- Open a Terminal and ```cd``` into the geoconnect repository.
- Run the following commands (May take a couple of minutes)

    ```
    mkvirtualenv geoconnect  
    pip install -r requirements/local.txt
    ```

- Mac note: If you run into Xcode (or other errors) when running the install, google it.  
  - Sometimes the [Xcode license agreement hasn't been accepted](http://stackoverflow.com/questions/26197347/agreeing-to-the-xcode-ios-license-requires-admin-privileges-please-re-run-as-r/26197363#26197363)

### Configure your virtualenv

* Edit the [postactivate script for the virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/scripts.html#postactivate).
  - Note: 'atom' may be any text editor

      ```
      atom $VIRTUAL_ENV/bin/postactivate
      ```

* On windows:

    ```
    atom %VIRTUAL_ENV%\Scripts\activate.bat
    ```

* Add these lines to the postactivate file and save the file
  - Mac:

      ```
      export DJANGO_DEBUG=True
      export DJANGO_SETTINGS_MODULE=geoconnect.settings.local
      ```

  - On windows:
      ```
      set "DJANGO_DEBUG=True"
      set "DJANGO_SETTINGS_MODULE=geoconnect.settings.local"
      ```

* Test the 'postactivate' script from the command line
  - Mac:

      ```
      deactivate
      workon geoconnect
      echo $DJANGO_SETTINGS_MODULE
      ```

  - Windows, use:

      ```
      echo %DJANGO_SETTINGS_MODULE%
      ```

  - You should see ```geoconnect.settings.local```


### Create/sync the database (still in ~\geoconnect)

Create a local sqlite database to store geoconnect information.

- Run this command (with your virtualenv activated):

```python manage.py migrate```

- To make the classification tables, run this (ignore any errors):

```python manage.py migrate --run-syncdb```

### Add initial data

- Add supported file types:
```
python manage.py loaddata --app registered_dataverse incoming_filetypes_initial_data.json
```

- Add layer classification colors
```
python manage.py loaddata --app layer_classification initial_data.json
```

### Create a superuser

- Use a username and password you'll use for local testing

```
python manage.py createsuperuser
```

### Run the local server and login to the admin screenshot

- Run the local server.  Use port 8070 so as not to overlap with Dataverse

```
python manage.py runserver 8070
```

- Got to the admin screen and login using your superuser credentials from the previous step:
  - http://127.0.0.1:8070/geo-connect-admin

### Register your local Dataverse

Once your are logged into the admin page from the previous step, register the Dataverse or Dataverses you would like to use for mapping.

  1. From the Admin page: scroll down, click on "Registered Dataverses"
  1. Top right: click "Add Registered Dataverse"
  1. Add a name and a url:
    - Localhost example:
      - Name: ```local dataverse```
      - Dataverse URL: ```http://localhost:8080```
    - HTTPS Example:
      - Name: ```beta.dataverse.org```
      - Dataverse URL: ```https://beta.dataverse.org:443```
      - Note: Follow the example above and add (```:443```) to the url
  1.  Save the registered Dataverse


### Add WorldMap credentials

  - Go to the directory: ```geoconnect/geoconnect/settings```
    1. Create a file named ```worldmap_secrets_local.json```
    1. Copy in the contents from ```template_worldmap_secrets.json```
  - Within the new file, add the information for a WorldMap account:
    - WORLDMAP_SERVER_URL: ```http://worldmap.harvard.edu```
    - WORLDMAP_ACCOUNT_USERNAME: ```(to be given in meeting)```
    - WORLDMAP_ACCOUNT_PASSWORD: ```(to be given in meeting)```


### Update your local Dataverse db to point to the local Geoconnect

- If you haven't used mapping yet, run this SQL query against Postgres:

```sql
INSERT INTO worldmapauth_tokentype (contactemail, hostname, ipaddress, mapitlink, name, timelimitminutes, timelimitseconds, md5, created, modified)
VALUES ('support@dataverse.org', '127.0.0.1:8070', '127.0.0.1:8070', 'http://127.0.0.1:8070/shapefile/map-it', 'GEOCONNECT', 30, 1800, '38c0a931b2d582a5c43fc79405b30c22', NOW(), NOW())
```

- If a ```GEOCONNECT``` entry already exists, use:

```sql
UPDATE worldmapauth_tokentype SET mapitlink = 'http://127.0.0.1:8070/shapefile/map-it' WHERE name = 'GEOCONNECT';
```
