import subprocess
"""
Start up Terminals for dev environment
"""

CMD_DICT =dict(\
    run_geoserver="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap;workon cga-worldmap;paver start_geoserver"\

    , run_geonode="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap;workon cga-worldmap;django-admin.py runserver  --settings=geonode.settings"\
    
    , run_geoconnect="cd /Users/rmp553/Documents/iqss-git/geoconnect/geoconnect;workon geoconnect;python manage.py runserver 8070"

    , shell_worldmap="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap/src/GeoNodePy/geonode;workon cga-worldmap;python manage.py shell --settings=geonode.settings"

    , run_tester_tabular="cd Documents/iqss-git/geoconnect-tester/tabular-api/code/;workon geo-tester;"
    , run_tester_shape="cd Documents/iqss-git/geoconnect-tester/geoconnect_tester/;workon geo-tester;mate Documents/iqss-git/geoconnect-tester/geoconnect_tester/"

    , edit_worldmap='charm /Users/rmp553/Documents/github-worldmap/cga-worldmap/'
    , edit_geoconnect='charm /Users/rmp553/Documents/iqss-git/geoconnect'
    , edit_shared_dv='charm /Users/rmp553/Documents/iqss-git/shared-dataverse-information'
              )

CMDS_ALL = CMD_DICT.keys()
CMDS_TEST = ('edit_shared_dv',)
CMDS_GEOCONNECT = ('run_geoconnect', 'edit_geoconnect', 'edit_shared_dv' )
CMDS_WORLDMAP = ('run_geoserver', 'run_geonode', 'shell_worldmap', 'edit_worldmap', 'edit_shared_dv' )
CMS_GEO_TEST_WORLDMAP = CMDS_WORLDMAP + ('run_geoconnect', 'edit_geoconnect')

def format_title(t):
    assert t is not None, 't cannot be None'
    return t.replace('_', ' ').title()
    
def build_subprocess_cmd_list(cmd_name, cmd_str, close_window=False):

    close_line = ''
    if close_window:
        close_line = '''delay 5
close (every window whose name contains "%s")
''' % (format_title(cmd_name))

    cmd_str = """tell application "Terminal"
tell settings set "Basic"
set title displays custom title to true
set custom title to "%s"
end tell
do script "%s"
%s
end tell
""" %  ( format_title(cmd_name), cmd_str, close_line)

    return ['osascript', '-e', '%s' % cmd_str ]


def run_terminals(cmd_list):
    global CMD_DICT
    assert isinstance(cmd_list, list) or isinstance(cmd_list, tuple), 'assert cmd_list must be a list or tuple'

    for cmd_name in cmd_list:
        assert CMD_DICT.has_key(cmd_name), "Command '%s' not found" % cmd

    for cmd_name in cmd_list:
        if cmd_name.startswith('run_') or cmd_name.startswith('shell_'):
            sublist = build_subprocess_cmd_list(cmd_name, CMD_DICT[cmd_name])
        else:
            sublist = build_subprocess_cmd_list(cmd_name, CMD_DICT[cmd_name])#, close_window=True)

        subprocess.call(sublist)

if __name__=='__main__':
    run_terminals(CMS_GEO_TEST_WORLDMAP)
    #run_terminals(CMDS_GEOCONNECT)
    #run_terminals(CMDS_WORLDMAP)
    #run_terminals(['run_tester_tabular', 'run_geonode'])
    #run_terminals(['edit_geoconnect', ])

"""
osascript -e 'tell app "Terminal"
 do script "cd /Users/rmp553/Documents/github-worldmap/cga-worldmap/src/GeoNodePy/geonode;workon cga-worldmap;charm ../../;python manage.py shell --settings=geonode.settings"
end tell'
"""