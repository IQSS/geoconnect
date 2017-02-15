


heroku config:set DISABLE_COLLECTSTATIC=1

git push heroku 3024-heroku:master


heroku run python manage.py migrate --settings=geoconnect.settings.heroku
heroku run python manage.py migrate --run-syncdb --settings=geoconnect.settings.heroku

heroku run python manage.py collectstatic --settings=geoconnect.settings.heroku --clear --no-input --verbosity=2


heroku run "python manage.py loaddata --app registered_dataverse incoming_filetypes_initial_data.json --settings=geoconnect.settings.heroku"

heroku run "python manage.py loaddata --app layer_classification initial_data.json --settings=geoconnect.settings.heroku"

heroku run "python manage.py loaddata --app registered_dataverse registered_dv_localhost.json --settings=geoconnect.settings.heroku"

heroku config:set DEBUG=0

heroku run "python manage.py remove_stale_data --email_notice --settings=geoconnect.settings.heroku"
