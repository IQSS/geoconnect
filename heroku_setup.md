
These notes describe setting up Geoconnect on a Heroku server using the Django settings in
"geoconnect.settings.heroku"

The steps assume that:
  1. You already have a Heroku account and that 
  1. The Geoconnect repository has been cloned to a local machine.

# Dashboard set-up

1. Install the Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
1. Log into the Heroku website
1. Create a new Heroku application
    - e.g. ```geoconnect-test```
1. Connect the Heroku application to your local repository
    - Open a local Terminal
    - cd into the top of the geoconnect repository
    - run ```heroku git:remote -a (Heroku app name)```
      - Example: ```heroku git:remote -a geoconnect-test```
    
# Install "Add-Ons"

Install the following Add-Ons.  Several of the Add-Ons will create config variables used by "geoconnect.settings.heroku".

From the Heroku dashboard, go to the "Resources" section.

## Install "Bucketeer"

  - The "Hobbyist" version is fine for testing
  - Config variables added to access S3 file storage:
    1. ```BUCKETEER_AWS_ACCESS_KEY_ID```
    1. ```BUCKETEER_AWS_SECRET_ACCESS_KEY```
    1. ```BUCKETEER_BUCKET_NAME```

## Install "Heroku Postgres"
  - The "Hobby Dev" or "Hobby Basic" version is fine for testing
  - Config variable added with database connection information:
    1. ```DATABASE_URL```


## Install "Heroku Scheduler"
  - The free version is fine
  - The scheduler is used for removing stale data and other "cron" type tasks
  - No config variables are added

## Install "SendGrid"
  - SendGrid is used for sending email messages to administrators
  - Config variable added:
    1. ```SENDGRID_USERNAME```
    1. ```SENDGRID_PASSWORD```
  -  **Setup**    
    1. Log into https://app.sendgrid.com using the config variables above
    1. Bottom left: Click "Settings -> API Keys"
    1. Top right: Click "Create API Key -> Generate API Key"
      - Name the key: "geoconnect_send"
      - Set full access for: "Mail Send -> Mail Send "
    1. Click "Save"
    1. Add the new key value to Heroku settings under ```SENDGRID_API_KEY```.
      - Use the web interface to add the key/value or
      - Use the Terminal to run:
        - ```heroku config:set SENDGRID_API_KEY=(key from sendgrid website)```

# Configure additional settings

Using the Heroku web interface or command line, set the following variables.
  1. *SECRET_KEY*
    - key: ```SECRET_KEY```
    - value: ```large random string```
      - See: https://docs.djangoproject.com/en/1.10/ref/settings/#secret-key
      - Methods for creating a key include:
        - code snippet: https://gist.github.com/mattseymour/9205591
        - online (not recommended): http://www.miniwebtool.com/django-secret-key-generator/
    - command line: ```heroku config:set SECRET_KEY=(secret key value)```
  1. *DJANGO_DEBUG*
    - Turn Django debug off.  Note: You may want to turn it on for troubleshooting.
    - key: ```DJANGO_DEBUG```
    - value: ```0```
    - command line: ```heroku config:set DJANGO_DEBUG=0```
  1. *DEBUG_COLLECTSTATIC*
    - key: ```DEBUG_COLLECTSTATIC```
    - value: ```1```
    - command line: ```heroku config:set DEBUG_COLLECTSTATIC=1```
  1. *WORLDMAP_ACCOUNT_USERNAME*
    - Username for a standard WorldMap account that belongs to the ```datavese``` group
    - key: ```WORLDMAP_ACCOUNT_USERNAME```
    - value: ```(worldmap username)```
    - command line: ```heroku config:set WORLDMAP_ACCOUNT_USERNAME=(worldmap username)```
  1. *WORLDMAP_ACCOUNT_PASSWORD*
    - key: ```WORLDMAP_ACCOUNT_PASSWORD```
    - value: ```(worldmap password)```
    - command line: ```heroku config:set WORLDMAP_ACCOUNT_PASSWORD=(worldmap password)```
  1. *WORLDMAP_SERVER_URL*
    - key: ```WORLDMAP_SERVER_URL```
    - value: ```http://worldmap.harvard.edu```
      - Currently, there is a single WorldMap installation
      - **Note**: Do not use a trailing ```/```
    - command line: ```heroku config:set WORLDMAP_SERVER_URL=http://worldmap.harvard.edu```
  1. *DATAVERSE_SERVER_URL*
    - key: ```DATAVERSE_SERVER_URL```
    - value: ```(url to dataverse app)```
      - example: ```https://dataverse.harvard.edu```
      - **Note**: Do not use a trailing ```/```
      - Note: Default Dataverse url in case of error. Unless there is a severe error, any registered dataverse may call a Geoconnect installation.
    - command line: ```heroku config:set DATAVERSE_SERVER_URL=(url to dataverse app)```
      - example: ```heroku config:set DATAVERSE_SERVER_URL=https://beta.dataverse.org```
  1. *HEROKU_SITEURL*
    - key: ```HEROKU_SITEURL```
    - value: ```(url to heroku app)```
      - example: ```https://geoconnect-test.herokuapp.com```
    - command line: ```heroku config:set HEROKU_SITEURL=(url to heroku app)```
      - example: ```heroku config:set HEROKU_SITEURL=https://geoconnect-test.herokuapp.com```
  1. *HEROKU_SERVER_NAME*
    - key: ```HEROKU_SERVER_NAME```
    - value: ```(heroku app server name)```
      - example: ```geoconnect-test.herokuapp.com```
    - command line: ```heroku config:set HEROKU_SITEURL=(heroku app server name)```
      - example: ```heroku config:set HEROKU_SERVER_NAME=geoconnect-test.herokuapp.com```


# Deploy and Initialize the App

## First time

  1. Disable collectstatic:
    - ```heroku config:set DISABLE_COLLECTSTATIC=1```
  1. Push the branch
    - Run: ```git push heroku master```
    - To push a specific branch:
      - ```git push heroku [your branch name]:master```
      - Example: ```git push heroku 3024-heroku:master```
  1. Run collectstatic manually:
    - ```heroku run 'python manage.py collectstatic --no-input --settings=geoconnect.settings.heroku'```      
  1. Create/sync the database:
    - ```heroku run 'python manage.py migrate --settings=geoconnect.settings.heroku'```
    - ```heroku run 'python manage.py migrate --run-syncdb --settings=geoconnect.settings.heroku'```
  1.  Add initial data:
    - ```heroku run 'python manage.py loaddata --app registered_dataverse incoming_filetypes_initial_data.json --settings=geoconnect.settings.heroku'```
    - ```heroku run 'python manage.py loaddata --app layer_classification initial_data.json --settings=geoconnect.settings.heroku'```
  1. ~~Enable collectstatic for future deployments:~~
      ~~- ```heroku config:set DISABLE_COLLECTSTATIC=0```~~


## Create a superuser and login to the Admin page

  1. Create a superuser:
    - ```heroku run 'python manage.py createsuperuser --settings=geoconnect.settings.heroku'```
  2. Open the admin web page:
    - ```heroku open /geo-connect-admin```
  3. Log in using your superuser credentials

## Register your Dataverse

Once your are on the admin page in the previous step, register the Dataverse or Dataverses you would like to use for mapping.

  1. From the Admin page: scroll down, click on "Registered Dataverses"
  1. Top right: click "Add Registered Dataverse"
  1. Add a name and a url.  Note the example below for https and the port added to the end (```:443```):
    - Example:
      - Name: beta.dataverse.org
      - Dataverse URL: https://beta.dataverse.org:443
   1.  Save the registered Dataverse

## Update the Geoconnect URL on your Dataverse Database

  1.  Go to the Postgres command line for your Dataverse
  1.  Update the ```worldmapauth_tokentype``` table as follows:
    - ```update worldmapauth_tokentype set mapitlink = '(url to heroku app)/shapefile/map-it', hostname='(heroku app server name)' where name = 'GEOCONNECT';```
    - Example using ```geoconnect-dev.herokuapp.com```:
      - ```update worldmapauth_tokentype set mapitlink = 'https://geoconnect-dev.herokuapp.com/shapefile/map-it', hostname='geoconnect-dev.herokuapp.com' where name = 'GEOCONNECT';```


# Add scheduler task: Stale data removal

The django command "remove_stale_data" deletes old objects and their associated files from geoconnect.

Initially, this should run every 24 hours via the Heroku Scheduler.

To set it up:

  1. Go to the Heroku Resources web page for your app
  1. Click on the "Heroku Scheduler"
  1. Click "Add New Job"
  1. Add the following command to the input box:
    - ```python manage.py remove_stale_data --really-delete --email-notice --settings=geoconnect.settings.heroku```
  1. This command will run a script to remove stale data.  The extra parameters work as follows:
    - ```-really-delete``` - actually delete stale objects and files.  Omitting this parameter will run the full script to check for files to delete--but not actually delete them.
    - ```--email-notice``` - email the results of the stale data check to the ADMINS in the Django settings file.  This works regardless of whether ```really-delete``` is used

To test it from the command line:

  - Testing from the command line:
  - without delete:
    - ```heroku run 'python manage.py remove_stale_data --email-notice --settings=geoconnect.settings.heroku'```
  - with delete:
      - ```heroku run 'python manage.py remove_stale_data --really-delete --email-notice --settings=geoconnect.settings.heroku'```

# Subsequent updates

Once the app has been set up, including the configuration variables and the database, subsequent updates to the Github repository may be deployed as follows:

## Push the branch
  - Run: ```git push heroku master```
  - To push a specific branch:
    - ```git push heroku [your branch name]:master```
    - Example: ```git push heroku 3024-heroku:master```

## Add new static files (if needed)
  - ```heroku run 'python manage.py collectstatic --no-input --settings=geoconnect.settings.heroku'```      

## Migrate database changes (if needed)

  - ```heroku run 'python manage.py migrate --settings=geoconnect.settings.heroku'```

- If the tables don't have migrations:

  - ```heroku run 'python manage.py migrate --run-syncdb --settings=geoconnect.settings.heroku'```
