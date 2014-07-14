
## Press classify

### Step 1: Describe features

Send a layer name to the geoserver and receive a list of attributes. Make this available via the API?

+ URL: 
    ```
http://localhost:8000/geoserver/wfs?&SERVICE=WFS&REQUEST=DescribeFeatureType&TYPENAME=geonode%3Aboston_social_disorder_pbl
    ```
+ TYPE: GET
 
+ GET Params (broken out):
    - Request: DescribeFeatureType
    - Service: WFS
    - TYPENAME: geonode:boston_social_disorder_pbl

+ Response

    + List of field names and variable types
    + Below is a list of variable types. This choice mapping { xml variable : js variable } is from from gxp.js, line 42:
    ```javascript
       {"xsd:boolean":"boolean","xsd:int":"int","xsd:integer":"int","xsd:short":"int","xsd:long":"int","xsd:date":"date","xsd:string":"string","xsd:float":"float","xsd:double":"float"}
    ```
    + Variable types which allow all "Method" choices (binning algorithms):
        - xsd:int 
        - xsd:integer
        - xsd:short
        - xsd:long
        - xsd:double
        - xsd:float
    + Variable type(s) which only classify by "Unique Values":
        + xsd:string
    + What classifications do these receive
        - xsd:boolean?
        - xsd:data?
       
     
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


#### Response questions:

1.  What other "xsd:" types are there?
1.  Algorithm types and color choices are few and can be placed in a configuration file.
    
    
### Step 2: Send style params and receive formatted rules


+ URL: 
    ```
http://localhost:8000/gs/rest/sldservice/geonode:boston_social_disorder_pbl/classify.xml?attribute=Violence_4&method=equalInterval&intervals=5&ramp=Gray&startColor=%23FEE5D9&endColor=%23A50F15&reverse=
    ```
    
+ TYPE: GET
 
+ GET Params (broken out):
 1. attribute:  Violence_4
 1. method:  equalInterval
 1. intervals:  5
 1. ramp:  Gray
 1. reverse:  (blank or true)
 1. startColor:  #FEE5D9
 1. endColor:  #A50F15

+ Response
    ```xml
    <Rules>
      <Rule>
        <Title> &gt; -2.7786 AND &lt;= 2.4966</Title>
        <Filter>
          <And>
            <PropertyIsGreaterThanOrEqualTo>
              <PropertyName>Violence_4</PropertyName>
              <Literal>-2.7786</Literal>
            </PropertyIsGreaterThanOrEqualTo>
            <PropertyIsLessThanOrEqualTo>
              <PropertyName>Violence_4</PropertyName>
              <Literal>2.4966</Literal>
            </PropertyIsLessThanOrEqualTo>
          </And>
        </Filter>
        <PolygonSymbolizer>
          <Fill>
            <CssParameter name="fill">#424242</CssParameter>
          </Fill>
          <Stroke/>
        </PolygonSymbolizer>
      </Rule>
      <Rule>
        <Title> &gt; 2.4966 AND &lt;= 7.7718</Title>
        <Filter>
          <And>
            <PropertyIsGreaterThan>
              <PropertyName>Violence_4</PropertyName>
              <Literal>2.4966</Literal>
            </PropertyIsGreaterThan>
            <PropertyIsLessThanOrEqualTo>
              <PropertyName>Violence_4</PropertyName>
              <Literal>7.7718</Literal>
            </PropertyIsLessThanOrEqualTo>
          </And>
        </Filter>
        <PolygonSymbolizer>
          <Fill>
            <CssParameter name="fill">#676767</CssParameter>
          </Fill>
          <Stroke/>
        </PolygonSymbolizer>
      </Rule>
      <Rule>
        <Title> &gt; 7.7718 AND &lt;= 13.047</Title>
        <Filter>
          <And>
            <PropertyIsGreaterThan>
              <PropertyName>Violence_4</PropertyName>
              <Literal>7.7718</Literal>
            </PropertyIsGreaterThan>
            <PropertyIsLessThanOrEqualTo>
              <PropertyName>Violence_4</PropertyName>
              <Literal>13.047</Literal>
            </PropertyIsLessThanOrEqualTo>
          </And>
        </Filter>
        <PolygonSymbolizer>
          <Fill>
            <CssParameter name="fill">#8B8B8B</CssParameter>
          </Fill>
          <Stroke/>
        </PolygonSymbolizer>
      </Rule>
      <Rule>
        <Title> &gt; 13.047 AND &lt;= 18.3222</Title>
        <Filter>
          <And>
            <PropertyIsGreaterThan>
              <PropertyName>Violence_4</PropertyName>
              <Literal>13.047</Literal>
            </PropertyIsGreaterThan>
            <PropertyIsLessThanOrEqualTo>
              <PropertyName>Violence_4</PropertyName>
              <Literal>18.3222</Literal>
            </PropertyIsLessThanOrEqualTo>
          </And>
        </Filter>
        <PolygonSymbolizer>
          <Fill>
            <CssParameter name="fill">#B0B0B0</CssParameter>
          </Fill>
          <Stroke/>
        </PolygonSymbolizer>
      </Rule>
      <Rule>
        <Title> &gt; 18.3222 AND &lt;= 23.5975</Title>
        <Filter>
          <And>
            <PropertyIsGreaterThan>
              <PropertyName>Violence_4</PropertyName>
              <Literal>18.3222</Literal>
            </PropertyIsGreaterThan>
            <PropertyIsLessThanOrEqualTo>
              <PropertyName>Violence_4</PropertyName>
              <Literal>23.5975</Literal>
            </PropertyIsLessThanOrEqualTo>
          </And>
        </Filter>
        <PolygonSymbolizer>
          <Fill>
            <CssParameter name="fill">#D4D4D4</CssParameter>
          </Fill>
          <Stroke/>
        </PolygonSymbolizer>
      </Rule>
    </Rules>
    ```
    
    
### Step 3: Set new style for layer

+ URL: 
    ```
http://localhost:8000/gs/rest/styles/boston_social_disorder_pbl.xml
    ```
+ TYPE: PUT
 
+ XML Data sent:
    ```xml
    <sld:StyledLayerDescriptor xmlns:sld="http://www.opengis.net/sld" version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml"><sld:NamedLayer><sld:Name>geonode:boston_social_disorder_pbl</sld:Name><sld:UserStyle><sld:Name>boston_social_disorder_pbl</sld:Name><sld:IsDefault>1</sld:IsDefault><sld:FeatureTypeStyle><sld:Rule><sld:Title> &gt; -2.7786 AND &lt;= 2.4966</sld:Title><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThanOrEqualTo><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>-2.7786</ogc:Literal></ogc:PropertyIsGreaterThanOrEqualTo><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>2.4966</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter><sld:PolygonSymbolizer><sld:Fill><sld:CssParameter name="fill">#424242</sld:CssParameter></sld:Fill><sld:Stroke><sld:CssParameter name="stroke">#ffbbbb</sld:CssParameter><sld:CssParameter name="stroke-width">0.7</sld:CssParameter></sld:Stroke></sld:PolygonSymbolizer></sld:Rule><sld:Rule><sld:Title> &gt; 2.4966 AND &lt;= 7.7718</sld:Title><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>2.4966</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>7.7718</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter><sld:PolygonSymbolizer><sld:Fill><sld:CssParameter name="fill">#676767</sld:CssParameter></sld:Fill><sld:Stroke><sld:CssParameter name="stroke">#ffbbbb</sld:CssParameter><sld:CssParameter name="stroke-width">0.7</sld:CssParameter></sld:Stroke></sld:PolygonSymbolizer></sld:Rule><sld:Rule><sld:Title> &gt; 7.7718 AND &lt;= 13.047</sld:Title><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>7.7718</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>13.047</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter><sld:PolygonSymbolizer><sld:Fill><sld:CssParameter name="fill">#8B8B8B</sld:CssParameter></sld:Fill><sld:Stroke><sld:CssParameter name="stroke">#ffbbbb</sld:CssParameter><sld:CssParameter name="stroke-width">0.7</sld:CssParameter></sld:Stroke></sld:PolygonSymbolizer></sld:Rule><sld:Rule><sld:Title> &gt; 13.047 AND &lt;= 18.3222</sld:Title><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>13.047</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>18.3222</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter><sld:PolygonSymbolizer><sld:Fill><sld:CssParameter name="fill">#B0B0B0</sld:CssParameter></sld:Fill><sld:Stroke><sld:CssParameter name="stroke">#ffbbbb</sld:CssParameter><sld:CssParameter name="stroke-width">0.7</sld:CssParameter></sld:Stroke></sld:PolygonSymbolizer></sld:Rule><sld:Rule><sld:Title> &gt; 18.3222 AND &lt;= 23.5975</sld:Title><ogc:Filter><ogc:And><ogc:PropertyIsGreaterThan><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>18.3222</ogc:Literal></ogc:PropertyIsGreaterThan><ogc:PropertyIsLessThanOrEqualTo><ogc:PropertyName>Violence_4</ogc:PropertyName><ogc:Literal>23.5975</ogc:Literal></ogc:PropertyIsLessThanOrEqualTo></ogc:And></ogc:Filter><sld:PolygonSymbolizer><sld:Fill><sld:CssParameter name="fill">#D4D4D4</sld:CssParameter></sld:Fill><sld:Stroke><sld:CssParameter name="stroke">#ffbbbb</sld:CssParameter><sld:CssParameter name="stroke-width">0.7</sld:CssParameter></sld:Stroke></sld:PolygonSymbolizer></sld:Rule></sld:FeatureTypeStyle></sld:UserStyle></sld:NamedLayer></sld:StyledLayerDescriptor>
    ```
    
+ Response
    + 200 - updated
    + 201 - created