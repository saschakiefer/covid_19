#!/bin/bash

ffmpeg -framerate 2 -start_number 5 -i 'frames/confirmed/frame_%6d.png' -c:v h264 -r 30 -s 1920x1080 -pix_fmt yuv420p -y ./videos/confirmed.mp4
ffmpeg -framerate 2 -start_number 5 -i 'frames/active/frame_%6d.png' -c:v h264 -r 30 -s 1920x1080 -pix_fmt yuv420p -y ./videos/active.mp4