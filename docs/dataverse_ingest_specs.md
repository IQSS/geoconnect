h2. More details regarding the shapefiles

A shapefile is a set of files, often uploaded/transferred in .zip format.  This set may contain up to 15 files.  A minimum of 3 specific files (.shp, .shx, .dbf) are needed to be a valid shapefile and a 4th file (.prj) is required for WorldMap--or any type of meaningful visualization.  

For ingest and connecting to WorldMap 4 files are the minimum required:

* .shp - shape format; the feature geometry itself
* .shx - shape index format; a positional index of the feature geometry to allow seeking forwards and backwards quickly
* .dbf - attribute format; columnar attributes for each shape, in dBase IV format
* .prj - projection format; the coordinate system and projection information, a plain text file describing the projection using well-known text format


h2. DV Ingest Specifics

# .zip is unpacked (same as all .zip files)
# shapefile sets are recognized by the same base name and specific extensions.
# Example.  These individual files constitute a shapefile set.  The first four are the minimum required (.shp, .shx, .dbf, .prj)
<pre>
- bicycles.shp    (required extension)
- bicycles.shx    (required extension)
- bicycles.prj	(required extension)
- bicycles.dbf	(required extension)
- bicycles.sbx	(NOT required extension)
- bicycles.sbn	(NOT required extension)
</pre>
# Upon recognition of the 4 required files, the dataverse will:
  * Group them _as well as any other relevant files into a shapefile set_
  * Create a new .zip with "mimetype" as a shapefile.
  * The shapefile set will persist as this new .zip
  * Connected to this new set, a shapefile metadata block will be created containing file info: name, size, date

h3. Example 1a: Original .zip contents

A file name is *bikes_and_subways.zip* is uploaded to the Dataverse. This .zip contains the following files.
<pre>
- bicycles.shp  (shapefile set #1)
- bicycles.shx  (shapefile set #1)
- bicycles.prj  (shapefile set #1)
- bicycles.dbf  (shapefile set #1)
- bicycles.sbx  (shapefile set #1)
- bicycles.sbn  (shapefile set #1)
- bicycles.txt
- the_bikes.md
- readme.txt
- subway_line.shp  (shapefile set #2)
- subway_line.shx  (shapefile set #2)
- subway_line.prj  (shapefile set #2)
- subway_line.dbf  (shapefile set #2)
</pre>		

h3. Example 1b: Unpacked files saved in DV

Upon ingest, the dataverse unpacks the file *bikes_and_subways.zip*.  Upon recognizing the shapefile sets, it groups those files together into new .zip files.

Effectively, the files making up shapefile set #1 become a new .zip; the files making up shapefile set #2 will become a new .zip. etc.  The remaining files  will stay as the are.

This is to ensure that a shapefile set remains intact--individual files are not deleted from a set, etc.

<pre>
- bicycles.zip  
	Contains shapefile set #1: bicycles.shp, 	bicycles.shx, bicycles.prj, bicycles.dbf, bicycles.sbx, bicycles.sbn)
</pre>			

* mimetype: "shapefile"; isType("shapefile") -> true
* metadata block: 
	
<pre>
[{ 
	"filename" : "bicycles.shp",
	"filesize" : 48596,
},
	{ 
	"filename" : "bicycles.shx",
	"filesize" : 13956,
}, ... etc ... ]</pre>

<pre>
- bicycles.txt  (separate, not part of a shapefile set)
- the_bikes.md  (separate, not part of a shapefile set)
- readme.txt  (separate, not part of a shapefile set)
- subway_line.zip  (contains shapefile set #2: subway_line.shp, subway_line.shx, subway_line.prj, subway_line.dbf)
</pre>

* mimetype: "shapefile"; isType("shapefile") -> true	
* metadata block: 

<pre>
[{ 
	"filename" : "subway_line.shp",
	"filesize" : 78526,
},
	{ 
	"filename" : "subway_line.shx",
	"filesize" :  956,
}, ... etc ... ]</pre>









