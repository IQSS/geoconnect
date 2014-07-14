
## Press classify

### Step 1: Describe features

Send a layer name to the geoserver and receive a list of attributes. Make this available via the API?

+ URL: http://localhost:8000/geoserver/wfs?&SERVICE=WFS&REQUEST=DescribeFeatureType&TYPENAME=geonode%3Aboston_social_disorder_pbl

+ TYPE: GET
 
+ GET Params (broken out):
    1. Request: DescribeFeatureType
    1. Service: WFS
    1. TYPENAME: geonode:boston_social_disorder_pbl

+ Response
```xml
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:base="http://capra.opengeo.org/base/" xmlns:geonode="http://geonode.org/" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:wfs="http://www.opengis.net/wfs/2.0" elementFormDefault="qualified" targetNamespace="http://geonode.org/">
<xsd:import namespace="http://www.opengis.net/gml/3.2" schemaLocation="http://localhost:8080/geoserver/schemas/gml/3.2.1/gml.xsd"></xsd:import>
<xsd:complexType name="boston_social_disorder_pblType">
<xsd:complexContent>
<xsd:extension base="gml:AbstractFeatureType">
<xsd:sequence>
<xsd:element maxOccurs="1" minOccurs="0" name="the_geom" nillable="true" type="gml:MultiSurfacePropertyType"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="OBJECTID" nillable="true" type="xsd:long"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="AREA" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="PERIMETER" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="STATE" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="COUNTY" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="TRACT" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="BLOCKGROUP" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="BG_ID" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="CT_ID" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="BLK_COUNT" nillable="true" type="xsd:int"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="LOGRECNO" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="DRY_ACRES" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="DRY_SQMI" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="DRY_SQKM" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SHAPE_AREA" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SHAPE_LEN" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="HOODS_PD_I" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Nbhd" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="NbhdCRM" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="NSA_ID" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="NSA_NAME" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="BG_ID_1" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Homeowners" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="MedIncomeH" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="propwhite" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="propblack" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="propasian" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="prophisp" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="medage" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="propcolleg" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="TotalPop" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="popden" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Type" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="ID2" nillable="true" type="xsd:int"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="BG_ID_12" nillable="true" type="xsd:string"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocDis_201" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocStrife_" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Alcohol_20" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Violence_2" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Guns_2010" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocStrife1" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocDis_202" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocStrif_1" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Alcohol_21" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Violence_3" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Guns_2011" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocStrif_2" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocDis_203" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocStrif_3" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Alcohol_22" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Violence_4" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="Guns_2012" nillable="true" type="xsd:double"></xsd:element>
<xsd:element maxOccurs="1" minOccurs="0" name="SocStrif_4" nillable="true" type="xsd:double"></xsd:element>
</xsd:sequence>
</xsd:extension>
</xsd:complexContent>
</xsd:complexType>
<xsd:element name="boston_social_disorder_pbl" substitutionGroup="gml:AbstractFeature" type="geonode:boston_social_disorder_pblType"></xsd:element>
</xsd:schema>
```
