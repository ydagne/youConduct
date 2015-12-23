# youConduct
Conduct a virtual orchestra using a webcam

YouConduct is a set of python script that allow you to conduct an orchestra of virtual instruments. YouConduct is based on two libraries: fluidSynth and OpenCV. FluidSynth is a software that synthesizes music from soundfont in real-time. OpenCV is known for powerful graphics processing in real-time.

In order to use youConduct, you need to install the following first:
  - fluidSynth 
  - opencv2
  - python binding for opencv

For debian distributions, you can install the above as follows:

    sudo apt-get install libopencv-dev python-opencv fluidsynth
  
# colorSound
colorSound lets you conduct using colors. It tracks three colors (Green, Blue, and Red) from a webcam. Each color plays different instrument. The soundfont that comes with youConduct ('soundFont1.sf2') has three presets. You can use other soundfont2 files if you want to play more instruments.

  - Green - Yamaha Grand Piano
  - Blue - Violin
  - Red - Ahh Choir
