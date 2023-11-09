# rpi-timelapse

This is a small script to get my pi to take a series of still photos for later assembly into a timelapse. There's many scripts out there like this.. but this one is mine.

It provides udev rules to trigger the timelapse when a usb device with an exfat file system is plugged in and will take images until the system is shut down or something goes wrong.

Also has some GPIO config to blink an LED light as a sort of status indicator. 

## Arguments

The script is configured with command line arguments. Run it with -h or read along:

```
  -p PATH, --path PATH  Directory to output images into. Will make timestamped subdirectories in this folder.
  -i INTERVAL, --interval INTERVAL
                        Seconds to delay between image captures. Default 1.3 seconds (fastest the 3B can capture without overruns.
  -s SIZE, --size SIZE  Size of image in WxH format. Default is sensor resolution.
```

## Requirements

Raspbian comes with most everything already set up, but you do need to add the python module:

```
apt install python3-picamera2
```

You can also do this by running the configure.yaml playbook.

# Interval Tips

I'm using the Camera Module 3 so these figures are based on that. But it's a safe bet the more pixels you capture the slower the script is gonna run. For my purposes I got these values:

* 4608x2592 (full resolution): 1.3 seconds
* 1920x1080: 0.3 seconds
* 1280x720: 0.15 seconds
* 640x480 or smaller: 0.1 seconds

You can specify faster with the script but if you want that might as well record a video.

As for choosing a good interval it depends on how fast stuff is moving. Photopills has a pretty good web based estimator out there: https://www.photopills.com/calculators/timelapse . Or if you can run their app they have a nice table of common subjects to refer to.

# Assembly

There's lots of tools out there to assemble time lapses, but I've taken to ffmpeg because it's simple and does a pretty good job.

## 60 fps output

```
ffmpeg -f image2 -r 60 -i image%09d.jpg -vcodec libx264 -crf 18 -pix_fmt yuv420p ../out-60.mp4
```

Change the -r parameter to suit.
