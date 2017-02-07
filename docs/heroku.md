


heroku config:set DISABLE_COLLECTSTATIC=1

git push heroku 3024-heroku:master

heroku run python manage.py collectstatic --settings=geoconnect.settings.heroku --clear --no-input
