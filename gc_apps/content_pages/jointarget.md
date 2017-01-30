### Possible Strategy: Require Data Formatting Before Table Upload

### Thoughts about formatting before table upload

1. API User (Dataverse system) is cleaning/formatting data
1. The Dataverse system needs to know *how* to clean/format the data for each JoinTarget.
1. GeoNode JoinTarget needs to provide some type of formatting information.
   1. How do you do this? (not sure of best path)
   
### Example (brainstorming)

1.  Change ```JoinTarget``` objects to have a **single Attribute** (instead of a M2M relation)
   - change: ```attributes = models.ManyToManyField(Attribute)```
   - to: ```attribute = models.ForeignKey(Attribute)```
1.  Require ```JoinTarget``` objects to specify a **JoinTargetFormatType**.  
    - This might be an FK to an object that specifies the Format.
    - Curator of the **JoinTargets** creates the **JoinTargetFormatTypes**--regulated by GeoNode admin
       - e.g. This is an expert user
    - For the API user (Dataverse system), the **JoinTargetFormatType** can offer information on what is expected
    - Very rough idea:
       - Note: ```regex_replacement_string```, ```python_code_snippet```, and ```tranformation_function_name``` are just brainstorming ideas
```python
class JoinTargetFormatType(models.Model)

    name = models.CharField(max_length=255, help_text='Census Tract (6 digits, no decimal)') 
    description_shorthand = models.CharField(max_length=255, help_text='dddddd') 
    clean_steps = models.TextField(help_text='verbal description. e.g. Remove non integers. Check for empty string. Pad with zeros until 6 digits.')
    
    # ??regex_replacement_string - could get ugly
    regex_replacement_string = models.CharField(help_text='"[^0-9]"; Usage: re.sub("[^0-9]", "", "1234.99"'\
                                , max_length=255)
    
    # ??python_code_snippet - dangerous - not to run directly
    #   
    #   val_list = [re.sub("[^0-9]", "", `x`) for x in val_list]
    #   val_list = [x for x in val_list if len(x) > 0]
    #   val_list = [x.zfill(6) for x in val_list if len(x) > 0]
    #
    python_code_snippet = models.TextField(blank=True)

    # ??tranformation_function_name - do cleaning on GeoNode side with a set of predefined transformation functions
    #
    #   Viable - e.g. Use top geospatial identifiers and formats
    #
    tranformation_function_name = models.CharField(max_length=255, blank=True, choices=TRANSFORMATION_FUNCTIONS)
  ```
