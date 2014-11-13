### Introduction

GeoConnect serves as an intermediate application between:

- [Dataverse](https://github.com/IQSS/dataverse) and 
- [WorldMap](https://github.com/cga-harvard/cga-worldmap).  

By using APIs on the Dataverse and WorldMap, GeoConnect serves the following broad functions:

1. Allows a Dataverse user to create a WorldMap map layer from a given Dataverse Datafile
    - Adds Dataverse information and links to the map layer metadata
    - Updates the Dataverse dataset with WorldMap metadata
1. Gives a Dataverse user the ability to style/classify the layer
    - In practical terms, styling involves choosing a variable, algorithm, and color to create a [chloropleth map](http://en.wikipedia.org/wiki/Choropleth_map)


The functionality is spread across 3 systems: Dataverse, GeoConnect, and the WorldMap.  The APIs are described below, system-by-system.

#### *Development Note*

*GeoConnect currently exists as a standalone web application.  An alternative method of implementing this functionality would be to build GeoConnect as an "app", directly using WorldMap functions rather than calling a custom built API.*

*However, at the time of this project, WorldMap was due for a major upgrade to [Geonode 2](http://geonode.org/2014/04/geonode-2-0/index.html).  Not knowing the timing of this upgrade, it was decided to implement functionality via API calls--with the thought of an easier transition once WorldMap was upgraded.  As of this writing, the Geonode 2 upgrade schedule has not been decided.*

*In addition, Dataverse was undergoing a full rewrite and the API "security" mechanism between GeoConnect and Dataverse is "evolving."*

### Dataverse APIs related to WorldMap

* 

