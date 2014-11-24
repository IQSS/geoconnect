#!/bin/sh
# This script should be wrapped by another script that
# encloses all of these commands in "scl enable python27"
# and is run by the "plaid" user one time for setup.
# i.e. scl enable python27 "path/to/this/script.sh"
# See also http://developerblog.redhat.com/2013/02/14/setting-up-django-and-python-2-7-on-red-hat-enterprise-6-the-easy-way/

#source /usr/bin/virtualenvwrapper.sh # python 2.6 version
source /opt/rh/python27/root/usr/bin/virtualenvwrapper.sh
#
# Setup virtualenv
echo "Setup virtualenv"
mkdir -p /webapps/virtualenvs
export WORKON_HOME=/webapps/virtualenvs
mkvirtualenv geoconnect
workon geoconnect
# Install requirements (pip)
echo "Install requirements (pip)"
cd /webapps/code/geoconnect
pip install -r requirements/production.txt
#
# Validate settings file
#
echo "Validate settings file"
cd /webapps/code/geoconnect/geoconnect
python manage.py validate --settings=geoconnect.settings.production
#
# Create sqlite database + initial tables
#
echo "Create sqlite database + initial tables"
python manage.py syncdb --noinput --settings=geoconnect.settings.production
#
echo "Create www directories (media/static/wsgi-related)"
mkdir /var/www/geoconnect/media # user uploads
mkdir /var/www/geoconnect/static # images, js, css, etc.
mkdir /var/www/geoconnect/geoconnect # wsgi.py
cp /webapps/code/geoconnect/geoconnect/geoconnect/vagrant-centos-wsgi.py /var/www/geoconnect/geoconnect/wsgi.py
#
echo "Run collecstatic to copy files to the static www directory"
#
python manage.py collectstatic --noinput --settings=geoconnect.settings.production
#python manage.py loaddata apps/classfication/fixtures/test-data.json --settings=geoconnect.settings.production
