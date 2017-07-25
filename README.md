# Geoconnect

Geoconnect is an application that integrates [Dataverse](http://datascience.iq.harvard.edu/dataverse) and the [Harvard WorldMap](http://worldmap.harvard.edu/), allowing researchers to visualize their geospatial data. Geoconnect can be used to create maps of shapefiles or of tabular files containing geospatial information.

The diagram below shows the relationship between Dataverse installations and the WorldMap:

[![Geoconnect diagram](readme_imgs/geoconnect.png?raw=true "Geoconnect")](https://geoconnect.datascience.iq.harvard.edu/)

For a full explanation of this functionality, please read the Dataverse guide:

  - [User perspective](http://guides.dataverse.org/en/latest/user/data-exploration/worldmap.html)
      - Includes screenshots of the user interface

The Geoconnect application is supported by the [Dataverse development team](https://dataverse.org/contact).


## I would like my Dataverse installation to use Geoconnect

_Note: To use Geoconnect, your Dataverse installation cannot be behind a firewall._

To use Geoconnect:

1. Email [support@dataverse.org](support@dataverse.org) with the full URL to your Dataverse installation.
1. Once you receive confirmation that the first step is completed, set these Dataverse settings to ```true```:
    - ```:GeoconnectCreateEditMaps```
    - ```:GeoconnectViewMaps```
    - See [Dataverse specific settings](http://guides.dataverse.org/en/latest/installation/config.html#geoconnectcreateeditmaps)
1. Make sure your Dataverse is pointing the correct Geoconnect server.
    - [Pointing to the Geoconnect ](http://guides.dataverse.org/en/latest/admin/geoconnect-worldmap.html)


## Installation Instructions

_Note: We recommend that you use the current production version of Geoconnect by following the section above._

Installation instructions are below:

    - [Local installation](https://github.com/IQSS/geoconnect/blob/master/local_setup.md)
    - [Heroku installation](https://github.com/IQSS/geoconnect/blob/master/heroku_setup.md)

### I would like to run Geoconnect myself but still use the Harvard WorldMap

This isn't recommended but is possible by following one of the installation instructions above and then doing the following:

  1. Create a Worldmap username/password: https://worldmap.harvard.edu/accounts/register/
  1. Contact WorldMap support (worldmap@harvard.edu) asking for the new username to be placed in the group ```dataverse```
  1. In the Geoconnect settings, update the following variable values to your WorldMap username/password.  
      - WORLDMAP_ACCOUNT_USERNAME
      - WORLDMAP_ACCOUNT_PASSWORD
    - Preferably add the values above as environment variables or in another secure method. Example: https://docs.djangoproject.com/en/1.11/topics/settings/#on-the-server-mod-wsgi
