

###  API call: Retrieve attributes for a layer

+ Send layer name to WorldMap API
    http://localhost:8000/gs/rest/sldservice/geonode:boston_social_disorder_pbl/attributes.xml
    
+ Receive layer field names/types in XML

###  API call: send styling params and receive new rules

+ Param list
  
(field name : example)

1. attribute: income
1. method:  equalInterval
1. intervals:  5
1. ramp:  Gray
1. reverse: (blank) or "true"
1. startColor:  #FEE5D9
1. endColor:  #A50F15

###  API call: Send new SLD