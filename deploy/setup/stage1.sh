#!/bin/sh
echo "Setting up geoconnect.org"
# Platform for
# Lightweight
# Applications from
# IQSS
# Data Science
useradd plaid
# EPEL already enabled on HMDC VM
rpm -Uvh http://dl.fedoraproject.org/pub/epel/6Server/x86_64/epel-release-6-8.noarch.rpm
# on HMDC VM, httpd is already installed
yum install -y httpd mod_wsgi ack elinks libjpeg-turbo-devel
rpm --import http://ftp.scientificlinux.org/linux/scientific/6.4/x86_64/os/RPM-GPG-KEY-sl
yum install -y http://ftp.scientificlinux.org/linux/scientific/6.4/x86_64/external_products/softwarecollections/yum-conf-softwarecollections-1.0-1.el6.noarch.rpm
#
# For compiling matplotlib
echo "gcc-c++"
yum install gcc-c++
yum install -y python27
echo "Setting up Django app with Python 2.7"
echo "Installing pip for Python 2.7"
scl enable python27 "easy_install pip"
echo "Install virtualenvwrapper"
scl enable python27 "pip install virtualenvwrapper"

echo "Setup virtualenv directory"
mkdir -p /webapps/virtualenvs
chown plaid /webapps/virtualenvs
mkdir /webapps/code
chown plaid /webapps/code

# Pull down shared-dataverse-information repository
#
cd /webapps/code
git clone https://github.com/IQSS/shared-dataverse-information.git
#

su plaid -l -s /bin/sh -c 'cd /webapps/code && cp -r /git/geoconnect .'
#su plaid -l -s /bin/sh -c 'cd /webapps/code'
cp /webapps/code/geoconnect/deploy/files/etc/sudoers.d/plaid /etc/sudoers.d
chmod 640 /etc/sudoers.d/plaid

cp /git/geoconnect/geoconnect/geoconnect/settings/secret_settings_prod.json /webapps/code/geoconnect/geoconnect/geoconnect/settings/geoconnect_settings_prod.json
chown plaid:apache /webapps/code/geoconnect/geoconnect/geoconnect/settings/secret_settings_prod.json
chmod 440 /webapps/code/geoconnect/geoconnect/geoconnect/settings/secret_settings_prod.json

#
# Create directory for sqlite db
#
echo "Create general data directory"
#
mkdir -p /webapps/data/geoconnect
chown apache /webapps/data/geoconnect

#
echo "Create data directory for sqlite db"
mkdir -p /webapps/data/geoconnect/sqlite
chown plaid:apache /webapps/data/geoconnect/sqlite
chmod 775 /webapps/data/geoconnect/sqlite

# Create a data directory for files (not on the web server path)
echo "Create data directory for shapefiles (not on the web server path)"

mkdir -p /webapps/data/geoconnect/geoconnect_files
chown plaid:apache /webapps/data/geoconnect/geoconnect_files
chmod 775 /webapps/data/geoconnect/geoconnect_files

#
echo "data directory for logs"
#
mkdir -p /webapps/data/geoconnect/geoconnect_files/logs
chown -R plaid:apache /webapps/data/geoconnect/geoconnect_files/logs
chmod -R 775 /webapps/data/geoconnect/geoconnect_files/logs

#
echo "data directory for shapefiles"
#
mkdir -p /webapps/data/geoconnect/geoconnect_files/dv_datafile_directory
chown plaid:apache /webapps/data/geoconnect/geoconnect_files/dv_datafile_directory
chmod 775 /webapps/data/geoconnect/geoconnect_files/dv_datafile_directory


#
echo "data directory for scratch work"
#
mkdir -p /webapps/data/geoconnect/geoconnect_files/gis_scratch_work
chown plaid:apache /webapps/data/geoconnect/geoconnect_files/gis_scratch_work
chmod 775 /webapps/data/geoconnect/geoconnect_files/gis_scratch_work



#
# configure apache
#
echo "Configure Apache"
cp /webapps/code/geoconnect/deploy/vagrant-centos-geoconnect.conf /etc/httpd/conf.d/geoconnect.conf
chown plaid /etc/httpd/conf.d/geoconnect.conf
cp -a /etc/sysconfig/httpd /etc/sysconfig/httpd.orig
cp /webapps/code/geoconnect/deploy/files/etc/sysconfig/httpd /etc/sysconfig/httpd
#
echo "Create /var/www directory owned by plaid"
mkdir /var/www/geoconnect
chown plaid /var/www/geoconnect
#
# Create directory for uploaded files
#
# echo "Create data directory for uploaded files"
#mkdir -p /webapps/data/geoconnect/geoconnect_uploaded_files
#chown apache /webapps/data/geoconnect/geoconnect_uploaded_files
#
# run main setup script as "plaid" user with python 2.7
#
su plaid -l -s /bin/sh -c 'scl enable python27 "/webapps/code/geoconnect/deploy/setup/stage2.sh"'
# Permissions for database
#
chown plaid:apache /webapps/data/geoconnect/sqlite/geoconnect.db3
chmod 660 /webapps/data/geoconnect/sqlite/geoconnect.db3
#
service httpd start
chkconfig httpd on
# on HMDC VM, changed SELinux to "permissive" in /etc/selinux/config
# reboot
