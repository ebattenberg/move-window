'''
script to swap windows between monitors and move windows around on the active monitor
'''
import subprocess as sp
import sys
import pdb
import re

# configuration ----------------------
MON0_SIZE = (1920,1080)
MON1_SIZE = (1920,1200)
MON0_OFFSET = (0,120)
MON1_OFFSET = (1920,0)
# ------------------------------------

if len(sys.argv) < 2:
    sys.exit('usage: python move_window.py {small_left,big_left,small_right,big_right}')

arg = sys.argv[1]

xrandr_info = sp.check_output(['xrandr'])
#xrandr_info = 'current 1920 x 1080,'
overall_size = re.search(r".*current (\d+) x (\d+),",xrandr_info).group(1,2)
overall_size = [int(x) for x in overall_size]
#print overall_size
win = sp.check_output(['xdotool', 'getactivewindow']).strip()
win_info = sp.check_output(['xwininfo','-id',win])

if overall_size[0] == MON0_SIZE[0]+MON1_SIZE[0]:
    num_monitors = 2
    monitor_size = [MON0_SIZE,MON1_SIZE]
    monitor_offset = [MON0_OFFSET,MON1_OFFSET]

    left_coord = int(re.search(r".*Absolute upper-left X: +(\d+)\n",win_info).group(1))
    if left_coord < monitor_offset[1][0]:
        active_monitor = 0
    else:
        active_monitor = 1
elif overall_size[0] == MON0_SIZE[0]:
    num_monitors = 1
    monitor_size = [MON0_SIZE]
    monitor_offset = [MON0_OFFSET]
    active_monitor = 0
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

    # move to upper left
    sp.check_call(['xdotool','windowmove',win,str(offset[0]),str(offset[1])])

    if arg == 'small_left':
        sp.check_call(['xdotool','windowsize',win,str(left_partition),str(desktop_h)])
    elif arg == 'big_left':
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
    else:
        sys.exit('usage: python move_window.py {small_left,big_left,small_right,big_right}')











