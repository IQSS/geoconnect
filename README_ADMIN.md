

## Maintenance mode

Geoconnect may be placed in maintenance mode via the administrative interface.  This is useful when either Dataverse or WorldMap is not available or undergoing maintenance.

### Step 1: Go to the geoconnect administrative interface.
### Step 2: Click Maintenance Mode
![admin page 1](readme_imgs/maint_mode_01.png?raw=true "admin page 1")
### Step 3: Click Maintenance Mode (again!)
![admin page 2](readme_imgs/maint_mode_02.png?raw=true "admin page 2")
### Step 4: Turn Maintenance mode on
  1. Check "is active"
  1. Set the date/time when the maintenance mode will end
      - Note: This date/time is for display only.  Maintenance mode needs to be turned off manually by unchecking "is active"
  1. Click "Save" on the top right
![admin page 3](readme_imgs/maint_mode_03.png?raw=true "admin page 3")
### Step 4: Users will now see a message similar to below when trying to view a map
![admin page 4](readme_imgs/maint_mode_04.png?raw=true "admin page 4")

## Mappable file types

_Note: Currently an API endpoint exists on the WorldMap to visualize Geotiff files.  However, the requisite Dataverse and Geoconnect code is not in place._

The mappability of different Dataverse file types can be switched on and off.  For example, the ability to map shapefiles may be turned off and the ability to view tabular files turned on.

![file types](readme_imgs/file_types.png?raw=true "file types")

  - For the current state of file types, see: https://geoconnect.datascience.iq.harvard.edu/dv/filetype-list/
  - To turn file mappability on/off, follow these steps:

### Step 1: Go to the geoconnect administrative interface.
### Step 2: Click "Incoming file type settings"
![file type 1](readme_imgs/file_type_admin_01.png?raw=true "file type 1")
### Step 3: Click the file type to change
![file type 2](readme_imgs/file_type_admin_02.png?raw=true "file type 2")
### Step 4: Change the setting
  1. Check "active" to enable/disable the file type
  2. Click "Save" on the top right
