move-window
===========

Python script to move windows around Ubuntu desktop using hotkeys

Requirements:
xdotool (in Ubuntu: sudo apt-get install xdotool)
xwininfo (part of X, I think)


Installation instructions:  
1. Install requirements  
2. move script to your ~/.scripts directory  
3. edit script with your monitor configuration (up to two monitors supported)  
	a. you can find your monitor sizes and offsets by running 'xrandr'  
4. To assign hotkeys to each command (in Ubuntu):   
	a. System Settings -> Keyboard -> Shortcuts -> Custom Shortcuts:  
	b. Add shortcuts, e.g.   
		Name: "Swap Monitors"  
		Command: "python /home/username/.scripts/move_window.py swap_monitors"  
		Click on right "accelerator" column to assign shortcut keys  

Available Commands:  
swap_monitors: move window to other monitor  
small_left: move window to left side of screen at 40% width, full height  
big_left: move window to left side of screen at 60% width, full height  
small_right: move window to right side of screen at 40% width, full height  
top_half: move window to top half of screen, full width  
bottom_half: move window to bottom half of screen, full width  
left_half: move window to left half of screen, full height  
right_half: move window to right half of screen, full height  
centered: move window to center of screen at 70% width, full height  
full: fullscreen  
autoconfig: generate json config file from xrandr

