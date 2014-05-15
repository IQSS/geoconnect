# geoconnect

Note: This is "proof of concept" code.  The design will change substantially--as will the logging, error checking, etc.

#### Purpose

[Boston Area Research Initiative](http://www.bostonarearesearchinitiative.net/) project to connect the [Dataverse](http://datascience.iq.harvard.edu/dataverse) to the [Worldmap](http://worldmap.harvard.edu/).  

#### Use Cases

* Add a GIS dataset to the Dataverse and send it to the WorldMap 
* On the WorldMap, search for datasets in a given geographic area for a specific time period

#### May be used in conjunction with [miniverse](https://github.com/IQSS/miniverse)

miniverse

	python manage.py runserver 8090
	
geoconnect

	python manage.py runserver