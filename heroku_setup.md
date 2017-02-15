
These notes describe setting up Geoconnect on a Heroku server using the Django settings in
"geoconnect.settings.heroku"

# Dashboard set-up

1. Install the Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
1. Create a new Heroku application
    - e.g. ```geoconnect-test```
1. Scroll down and look for "Existing Git repository"
    - Open a Terminal
    - cd into the top of the geoconnect repository
    - run ```heroku git:remote -a geoconnect-test```

# Install "Add-Ons"

Install the following Add-Ons.  Most of the Add-Ons will create environment settings used "geoconnect.settings.heroku".

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
    - command line: ```heroku config:set WORLDMAP_SERVER_URL=http://worldmap.harvard.edu```


heroku config:set HEROKU_SITEURL=https://geoconnect-dev.herokuapp.com
heroku config:set HEROKU_SERVER_NAME=geoconnect-dev.herokuapp.com


# Add scheduler task

# Stale data remover: python manage.py remove_stale_data --really-delete --email-notice --settings=geoconnect.settings.heroku
