import subprocess
"""
Start up Terminals for dev environment
"""

CMD_DICT =dict(\
    run_geoserver="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap;workon cga-worldmap;paver start_geoserver"\

    , run_geonode="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap;workon cga-worldmap;paver start_geoserver"\
    , run_geoconnect="cd /Users/rmp553/Documents/iqss-git/geoconnect/geoconnect;workon geoconnect;python manage.py runserver 8070"

    , shell_worldmap="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap/src/GeoNodePy/geonode;workon cga-worldmap;python manage.py shell --settings=geonode.settings"

    , run_tester_tabular="cd Documents/iqss-git/geoconnect-tester/tabular-api/code/;workon geo-test;"
    , run_tester_shape="cd Documents/iqss-git/geoconnect-tester/geoconnect_tester/;workon geo-test;"

    , charm_worldmap='charm /Users/rmp553/Documents/github-worldmap/cga-worldmap/'
    , charm_geoconnect='charm /Users/rmp553/Documents/iqss-git/geoconnect'
    , charm_shared_dv='charm /Users/rmp553/Documents/iqss-git/shared-dataverse-information'
              )

CMDS_ALL = CMD_DICT.keys()
CMDS_TEST = ('charm_shared_dv',)
CMDS_GEOCONNECT = ('run_geoconnect', 'charm_geoconnect', 'charm_shared_dv' )
CMDS_WORLDMAP = ('run_geoserver', 'run_geonode', 'shell_worldmap', 'charm_worldmap', 'charm_shared_dv' )


def build_subprocess_cmd_list(cmd_name, cmd_str, close_window=False):

    close_line = ''
    if close_window:
        close_line = '''delay 4
close front window without saving
'''

    cmd_str = """tell application "Terminal"
tell settings set "Basic"
set title displays custom title to true
set custom title to "%s"
end tell
do script "%s"
%s
end tell
""" %  ( cmd_name, cmd_str, close_line)

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
            sublist = build_subprocess_cmd_list(cmd_name, CMD_DICT[cmd_name], close_window=True)

        subprocess.call(sublist)

if __name__=='__main__':
    #run_terminals(CMDS_TEST)
    #run_terminals(CMDS_GEOCONNECT)
    run_terminals(CMDS_WORLDMAP)

"""
osascript -e 'tell app "Terminal"
 do script "cd /Users/rmp553/Documents/github-worldmap/cga-worldmap/src/GeoNodePy/geonode;workon cga-worldmap;charm ../../;python manage.py shell --settings=geonode.settings"
end tell'
"""