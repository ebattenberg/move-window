'''
script to swap windows between monitors and move windows around on the active monitor
'''
import subprocess as sp
import sys
import pdb
import json
import re
import os

# ------------------------------------------
# constants
# ------------------------------------------

config_filepath = os.path.expanduser('~/.scripts/move_window_conf.json')
usage = 'usage: python move_window.py {small_left,big_left,small_right,big_right,autoconfig}'

# ------------------------------------------
# helper functions 
# ------------------------------------------

def get_autoconfig(config_filepath):
    config = {}
    xrandr_info = sp.check_output(['xrandr'])
    #xrandr_info = 'current 1920 x 1080,'
    primary_match = re.search(
            r' connected primary (\d+)x(\d+)\+(\d+)\+(\d+) ',
            xrandr_info)
    if primary_match:
        p1,p2,p3,p4 = primary_match.group(1,2,3,4)
        config['mon0_size'] = (int(p1),int(p2))
        config['mon0_offset'] = (int(p3),int(p4))
    else:
        print 'unable to find primary monitor size'
        config['mon0_size'] = (0,0)
        config['mon0_offset'] = (0,0)

    secondary_match = re.search(
            r' connected (\d+)x(\d+)\+(\d+)\+(\d+) ',
            xrandr_info)
    if secondary_match:
        s1,s2,s3,s4 = secondary_match.group(1,2,3,4)
        if not primary_match:
            print 'using secondary monitor size for primary configuration'
            config['mon1_size'] = config['mon0_size']
            config['mon1_offset'] = config['mon0_offset']
            config['mon0_size'] = (int(s1),int(s2))
            config['mon0_offset'] = (int(s3),int(s4))
        else:
            config['mon1_size'] = (int(s1),int(s2))
            config['mon1_offset'] = (int(s3),int(s4))
    else:
        print 'unable to find monitor size'
        config['mon1_size'] = (0,0)
        config['mon1_offset'] = (0,0)

    config['right_primary'] = True

    overall_size = re.search(r" current (\d+) x (\d+),",xrandr_info).group(1,2)
    config['overall_size'] = tuple(int(x) for x in overall_size)

    return config

# ------------------------------------------
# arguments
# ------------------------------------------


if len(sys.argv) < 2:
    sys.exit(usage)

arg = sys.argv[1]

if arg == 'autoconfig':
    # create conf from xrandr
    config = get_autoconfig(config_filepath)
    json.dump(config,open(config_filepath,'w'),indent=4)
    print 'created config file at %s' % config_filepath
    sys.exit()

# ------------------------------------------
# config
# ------------------------------------------

try:
    config = json.load(open(config_filepath))
except IOError:
    # create conf from xrandr
    print ''
    print 'move_window.py: missing config file at %s' % config_filepath
    print 'run "python move_window.py autoconfig" to create the config file'
    print ''
    sys.exit()


# ------------------------------------
# params
# ------------------------------------
MON0_SIZE = config['mon0_size']
MON1_SIZE = config['mon1_size']
MON0_OFFSET = config['mon0_offset']
MON1_OFFSET = config['mon1_offset']
OVERALL_SIZE = config['overall_size']
RIGHT_PRIMARY = config['right_primary']


# -------------------------------------------
# main
# -------------------------------------------



win = sp.check_output(['xdotool', 'getactivewindow']).strip()
win_info = sp.check_output(['xwininfo','-id',win])

if OVERALL_SIZE[0] == MON0_SIZE[0]:
    num_monitors = 1
    monitor_size = [MON0_SIZE]
    monitor_offset = [MON0_OFFSET]
    active_monitor = 0
elif OVERALL_SIZE[0] == MON0_SIZE[0]+MON1_SIZE[0]:
    num_monitors = 2
    monitor_size = [MON0_SIZE,MON1_SIZE]
    monitor_offset = [MON0_OFFSET,MON1_OFFSET]


    left_coord = int(re.search(r".*Absolute upper-left X: +(\d+)\n",win_info).group(1))
    if RIGHT_PRIMARY:
        if left_coord < monitor_offset[0][0]:
            active_monitor = 1
        else:
            active_monitor = 0
    else:
        if left_coord < monitor_offset[1][0]:
            active_monitor = 0
        else:
            active_monitor = 1
else:
    raise ValueError, 'unsupported overall_size'



if arg == 'swap_monitors':
    if num_monitors > 1:
        new_x = monitor_offset[1-active_monitor][0]
        new_y = monitor_offset[1-active_monitor][1]

        # make sure window size fits in other monitor
        other_h = monitor_size[1-active_monitor][1]
        sp.check_call(['xdotool','windowsize',win,'x',str(other_h-100)])

        # move to upper left of other monitor
        sp.check_call(['xdotool','windowmove',win,str(new_x),str(new_y)])

else:

    offset = monitor_offset[active_monitor]
    desktop_w = monitor_size[active_monitor][0]
    desktop_h = monitor_size[active_monitor][1]
    
    # boundaries for small/big left/right 
    left_partition= int(desktop_w * 0.4)
    right_partition= int(desktop_w * 0.6)

    middle_height = int(desktop_h * 0.5)
    middle_width = int(desktop_w * 0.5)

    # boundaries for centered but not maximized
    boarder_left = int(desktop_w * 0.15)
    boarder_right = int(desktop_w * 0.85)
    if arg == 'info':
        print '---------------------------'
        print 'Desktop info '
        print '---------------------------'
        print 'Active monitor: ', active_monitor
        print 'Offset: ', offset
        print '---------------------------'
        print ''

    else:

        if arg == 'small_left':
            sp.check_call(['xdotool','windowmove',win,str(offset[0]),str(offset[1])])
            sp.check_call(['xdotool','windowsize',win,str(left_partition),str(desktop_h)])
        elif arg == 'big_left':
            sp.check_call(['xdotool','windowmove',win,str(offset[0]),str(offset[1])])
            sp.check_call(['xdotool','windowsize',win,str(right_partition),str(desktop_h)])
        elif arg == 'small_right':
            width = desktop_w - right_partition
            sp.check_call(['xdotool','windowsize',win,str(width),str(desktop_h)])
            sp.check_call(['xdotool','windowmove',win,str(offset[0]+right_partition),str(offset[1])])
        elif arg == 'big_right':
            width = desktop_w - left_partition
            sp.check_call(['xdotool','windowsize',win,str(width),str(desktop_h)])
            sp.check_call(['xdotool','windowmove',win,str(offset[0]+left_partition),str(offset[1])])
        elif arg == 'top_half':
            sp.check_call(['xdotool','windowsize',win,str(desktop_w),str(middle_height)])
        elif arg == 'bottom_half':
            height = desktop_h - middle_height
            sp.check_call(['xdotool','windowsize',win,str(desktop_w),str(height)])
            sp.check_call(['xdotool','windowmove',win,str(offset[0]),str(offset[1]+middle_height)])
        elif arg == 'left_half':
            sp.check_call(['xdotool','windowsize',win,str(middle_width),str(desktop_h)])
        elif arg == 'right_half':
            width = desktop_w - middle_width
            sp.check_call(['xdotool','windowsize',win,str(width),str(desktop_h)])
            sp.check_call(['xdotool','windowmove',win,str(offset[0]+middle_width),str(offset[1])])
        elif arg == 'centered':
            width = boarder_right - boarder_left
            sp.check_call(['xdotool','windowsize',win,str(width),str(desktop_h)])
            sp.check_call(['xdotool','windowmove',win,str(offset[0]+boarder_left),str(offset[1])])
        elif arg == 'full':
            sp.check_call(['xdotool','windowsize',win,str(desktop_w),str(desktop_h)])
        elif arg == 'term':
            sys.exit('term not implemented')
        else:
            sys.exit(usage)











