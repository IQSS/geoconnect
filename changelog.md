# Change Log

## [0.5.0](https://github.com/iqss/geoconnect) (2017-01-30)

### Django upgrade from 1.6 to 1.10

- Updates to shared-dataverse-information dependency
- For HttpRepsonse, changed ```mimetype=``` to ```content_type=```
- Upgraded django-debug-toolbar version from 1.0.1 to 1.6
- Removed old django.conf.urls.patterns--used lists of urls
- Changed ```render_to_response``` to ```render```, remove imports of ```RequestContext```
- Use ```TEMPLATES``` setting from django conf files
- Templates, use ```static``` tag
- Remove old models from worldmap_connect: WorldMapImportAttempt, WorldMapImportFail, WorldMapLayerInfo
- Switch ```datetime.now()``` to ```timezone.now()```
    - using ```from django.utils import timezone```
- Move geo_utils directory under gc_apps
- Move gc_apps directory to the top level
- Create initial migration files
  - If tables exist, run ```python manage.py  migrate --fake-initial```

### UI update

- Updated format of tabular mapping UI including workflow and layout.
