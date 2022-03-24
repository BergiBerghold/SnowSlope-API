#! /bin/bash

apt-get update
apt-get install -y g++
apt-get install -y libgdal-dev
apt-get install -y gdal-bin=2.1.2+dfsg-5+deb9u1
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

pip install gdal==2.1.3
