
#!/bin/sh

echo 'Compiling and Installing the Tello Video Stream module'

brew update


# install cmake

brew install cmake



# install dependencies

brew install boost

brew install boost-python

brew install ffmpeg

brew install tcl-tk

sudo pip install numpy --ignore-installed

sudo pip install matplotlib --ignore-installed

sudo pip install pillow --ignore-installed

sudo pip install opencv-python --ignore-installed



# pull and build h264 decoder library

cd h264decoder


mkdir build

cd build

cmake ..

make



# copy source .so file to tello.py directory

cp libh264decoder.so ../../



echo 'Compilation and Installation Done!'
