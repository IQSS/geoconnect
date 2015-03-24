import sys
import subprocess
from collections import OrderedDict
"""
Start up Terminals for dev environment
"""

CMD_DICT =dict(
    run_geoserver="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap;workon cga-worldmap;paver start_geoserver"

    , run_geonode="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap;workon cga-worldmap;django-admin.py runserver  --settings=geonode.settings"
    
    , run_geoconnect="cd /Users/rmp553/Documents/iqss-git/geoconnect/geoconnect;workon geoconnect;python manage.py runserver 8070"

    # Dataverse
    , run_dataverse_solr="cd Documents/solr-4.6.0/example/;java -jar start.jar"
    , shell_dataverse="cd NetBeansProjects/dataverse"
    , open_netbeans='open "/Applications/NetBeans/NetBeans 8.0.1.app"'
    , open_pgadmin3='open /Applications/pgAdmin3.app'
    , shell_query_counter='cd Documents/iqss-git/glassfish-query-counter/scripts/;python count_queries.py'
    
    # WorldMap
    , shell_worldmap="cd /Users/rmp553/Documents/github-worldmap/cga-worldmap/src/GeoNodePy/geonode;workon cga-worldmap;python manage.py shell --settings=geonode.settings"

    , run_tester_tabular="cd Documents/iqss-git/geoconnect-tester/tabular-api/code/;workon geo-tester;"
    , run_tester_shape="cd Documents/iqss-git/geoconnect-tester/geoconnect_tester/;workon geo-tester;mate Documents/iqss-git/geoconnect-tester/geoconnect_tester/"

    , edit_worldmap='charm /Users/rmp553/Documents/github-worldmap/cga-worldmap/'
    , edit_geoconnect='charm /Users/rmp553/Documents/iqss-git/geoconnect'
    , edit_shared_dv='charm /Users/rmp553/Documents/iqss-git/shared-dataverse-information'
 )

def get_command_lookup():
    
    cmds = OrderedDict()
    cmds['GeoConnect (Run/Edit)'] = ('run_geoconnect', 'edit_geoconnect', 'edit_shared_dv' )
    cmds['WorldMap (Run/Edit)'] = ('run_geoserver', 'run_geonode', 'shell_worldmap', 'edit_worldmap', 'edit_shared_dv' )
    cmds['Dataverse (Run/Edit)'] = ( 'run_dataverse_solr', 'open_pgadmin3', 'shell_dataverse', 'open_netbeans', 'shell_query_counter')
    cmds['GEO Test WorldMap'] = cmds['WorldMap (Run/Edit)'] + ('run_geoconnect', 'edit_geoconnect')
    #cmds['Dataverse (Run/Edit)'] = ('open_netbeans',)
    
    return cmds

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
    args = sys.argv
    if not len(args)==2:
        option_list = []
        for cnt, key in enumerate(get_command_lookup().keys(), 1):
            option_list.append('%d - %s' % (cnt, key))
        
        print """
------------------------------
Open Development Windows
------------------------------

Please choose an option: 

%s

------------------------------
""" % ('\n'.join(option_list))
    else:
        chosen_opt = args[1]
        assert chosen_opt.isdigit(), 'Please enter a number from the choice list.  "%s" is not a valid choice.' % (chosen_opt)
        chosen_opt = int(chosen_opt)
        
        option_lookup = {}
        for cnt, key in enumerate(get_command_lookup().keys(), 1):
            option_lookup[cnt] = key
        assert chosen_opt in option_lookup.keys(), 'Please enter a number from the choice list.  "%s" is not a valid choice.' % (chosen_opt)
        
        cmd_list = get_command_lookup().get(option_lookup[chosen_opt], None)
        assert cmd_list is not None, "cmd_list is None! For option '%s'" % option_lookup[chosen_opt]
        
        run_terminals(cmd_list)
            
    #run_terminals(CMS_GEO_TEST_WORLDMAP)
    #run_terminals(CMDS_GEOCONNECT)
    #run_terminals(CMDS_WORLDMAP)
    #run_terminals(['run_tester_tabular', 'run_geonode'])
    #run_terminals(['edit_geoconnect', ])

"""
osascript -e 'tell app "Terminal"
 do script "cd /Users/rmp553/Documents/github-worldmap/cga-worldmap/src/GeoNodePy/geonode;workon cga-worldmap;charm ../../;python manage.py shell --settings=geonode.settings"
end tell'
"""