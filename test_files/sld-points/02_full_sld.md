
- SLD info

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
   <sld:NamedLayer>
      <sld:Name>geonode:centroid_alt_qkh</sld:Name>
      <sld:UserStyle>
         <sld:Name>centroid_alt_qkhv_i_c_s_5_s</sld:Name>
         <sld:IsDefault>1</sld:IsDefault>
         <sld:FeatureTypeStyle>
            <sld:Rule>
               <sld:Title>&amp;gt; 0.0 AND &amp;lt;= 6.0</sld:Title>
               <ogc:Filter>
                  <ogc:And>
                     <ogc:PropertyIsGreaterThanOrEqualTo>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>0.0</ogc:Literal>
                     </ogc:PropertyIsGreaterThanOrEqualTo>
                     <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>6.0</ogc:Literal>
                     </ogc:PropertyIsLessThanOrEqualTo>
                  </ogc:And>
               </ogc:Filter>
               <sld:PointSymbolizer>
                  <sld:Graphic>
                     <sld:Mark>
                        <sld:WellKnownName>x</sld:WellKnownName>
                        <sld:Fill>
                           <sld:CssParameter name="fill">#FFF5F0</sld:CssParameter>
                        </sld:Fill>
                        <sld:Stroke>
                           <sld:CssParameter name="stroke">#ffffbb</sld:CssParameter>
                        </sld:Stroke>
                     </sld:Mark>
                     <sld:Size>10</sld:Size>
                  </sld:Graphic>
               </sld:PointSymbolizer>
            </sld:Rule>
            <sld:Rule>
               <sld:Title>&amp;gt; 6.0 AND &amp;lt;= 12.0</sld:Title>
               <ogc:Filter>
                  <ogc:And>
                     <ogc:PropertyIsGreaterThan>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>6.0</ogc:Literal>
                     </ogc:PropertyIsGreaterThan>
                     <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>12.0</ogc:Literal>
                     </ogc:PropertyIsLessThanOrEqualTo>
                  </ogc:And>
               </ogc:Filter>
               <sld:PointSymbolizer>
                  <sld:Graphic>
                     <sld:Mark>
                        <sld:WellKnownName>x</sld:WellKnownName>
                        <sld:Fill>
                           <sld:CssParameter name="fill">#E0C4C2</sld:CssParameter>
                        </sld:Fill>
                        <sld:Stroke>
                           <sld:CssParameter name="stroke">#ffffbb</sld:CssParameter>
                        </sld:Stroke>
                     </sld:Mark>
                     <sld:Size>10</sld:Size>
                  </sld:Graphic>
               </sld:PointSymbolizer>
            </sld:Rule>
            <sld:Rule>
               <sld:Title>&amp;gt; 12.0 AND &amp;lt;= 18.0</sld:Title>
               <ogc:Filter>
                  <ogc:And>
                     <ogc:PropertyIsGreaterThan>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>12.0</ogc:Literal>
                     </ogc:PropertyIsGreaterThan>
                     <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>18.0</ogc:Literal>
                     </ogc:PropertyIsLessThanOrEqualTo>
                  </ogc:And>
               </ogc:Filter>
               <sld:PointSymbolizer>
                  <sld:Graphic>
                     <sld:Mark>
                        <sld:WellKnownName>x</sld:WellKnownName>
                        <sld:Fill>
                           <sld:CssParameter name="fill">#C29395</sld:CssParameter>
                        </sld:Fill>
                        <sld:Stroke>
                           <sld:CssParameter name="stroke">#ffffbb</sld:CssParameter>
                        </sld:Stroke>
                     </sld:Mark>
                     <sld:Size>10</sld:Size>
                  </sld:Graphic>
               </sld:PointSymbolizer>
            </sld:Rule>
            <sld:Rule>
               <sld:Title>&amp;gt; 18.0 AND &amp;lt;= 24.0</sld:Title>
               <ogc:Filter>
                  <ogc:And>
                     <ogc:PropertyIsGreaterThan>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>18.0</ogc:Literal>
                     </ogc:PropertyIsGreaterThan>
                     <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>24.0</ogc:Literal>
                     </ogc:PropertyIsLessThanOrEqualTo>
                  </ogc:And>
               </ogc:Filter>
               <sld:PointSymbolizer>
                  <sld:Graphic>
                     <sld:Mark>
                        <sld:WellKnownName>x</sld:WellKnownName>
                        <sld:Fill>
                           <sld:CssParameter name="fill">#A36267</sld:CssParameter>
                        </sld:Fill>
                        <sld:Stroke>
                           <sld:CssParameter name="stroke">#ffffbb</sld:CssParameter>
                        </sld:Stroke>
                     </sld:Mark>
                     <sld:Size>10</sld:Size>
                  </sld:Graphic>
               </sld:PointSymbolizer>
            </sld:Rule>
            <sld:Rule>
               <sld:Title>&amp;gt; 24.0 AND &amp;lt;= 30.0</sld:Title>
               <ogc:Filter>
                  <ogc:And>
                     <ogc:PropertyIsGreaterThan>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>24.0</ogc:Literal>
                     </ogc:PropertyIsGreaterThan>
                     <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>symbol</ogc:PropertyName>
                        <ogc:Literal>30.0</ogc:Literal>
                     </ogc:PropertyIsLessThanOrEqualTo>
                  </ogc:And>
               </ogc:Filter>
               <sld:PointSymbolizer>
                  <sld:Graphic>
                     <sld:Mark>
                        <sld:WellKnownName>x</sld:WellKnownName>
                        <sld:Fill>
                           <sld:CssParameter name="fill">#85313A</sld:CssParameter>
                        </sld:Fill>
                        <sld:Stroke>
                           <sld:CssParameter name="stroke">#ffffbb</sld:CssParameter>
                        </sld:Stroke>
                     </sld:Mark>
                     <sld:Size>10</sld:Size>
                  </sld:Graphic>
               </sld:PointSymbolizer>
            </sld:Rule>
         </sld:FeatureTypeStyle>
      </sld:UserStyle>
   </sld:NamedLayer>
</sld:StyledLayerDescriptor>
```
