# Change Log

## [0.5.0](https://github.com/iqss/geoconnect) (2017-01-30)

** Django upgrade from 1.6 to 1.10 **

- Updates to shared-dataverse-information dependency
- For HttpRepsonse, changed ```mimetype=``` to ```content_type=```
- Upgraded django-debug-toolbar version from 1.0.1 to 1.6
- Removed old django.conf.urls.patterns--used lists of urls
- Changed ```render_to_response``` to ```render```, remove imports of ```RequestContext```
- Use ```TEMPLATES``` setting from django conf files
- Templates, use ```static``` tag

- [ ] Updated fixtures

** UI update **

- Updated format of tabular mapping UI including workflow and layout.
