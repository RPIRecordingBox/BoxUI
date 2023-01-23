#!/bin/bash -l
# Run this script as root!

# Required for qt to not instantly die
export XAUTHORITY=/run/user/1000/gdm/Xauthority
export DISPLAY=:0
export XDG_DATA_DIRS=/usr/local/share:/usr/share:/var/lib/snapd/desktop
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin

# Required for program SUDO check
export SUDO_UID=1000

cd /home/box1/opencv-camera-test/recording-demo/

date > out.txt
python3 main.py >> out.txt 2>&1