# Kai-Drone

## Background info
the Kai Drone will be a autonomous hexacopter, used to automatically detect specified objects within a pre-set flightpath.

## current challenges
1. detect barcodes
1. detect objects via [cloud vision](https://cloud.google.com/vision/)
1. indoor positioning
1. auto flight
1. obstacle avoidance
1. auto-dock

## Tools used

### Brains:
1. Raspberry Pi
1. Camera Module
1. OpenCV
1. custom Python scripting
1. [ROS integration](http://www.ros.org)

### Hardware
1. Hexacopter (DJI F550)
1. Flight controller
1. [IPS solution](https://en.wikipedia.org/wiki/Indoor_positioning_system)

## instructions for openCV

### setup
follow [these instructions](https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/) to setup your Pi

### usage
connect via VNC to your PI.  
for ease of use also have a ssh connection open.

load your profile  
`source .profile`

make sure to work in your virtual enviroment  
`workon cv`

currently, the images are sent to the x session you connect to through VNC, so it's not 100% headless yet.
