#! /bin/bash

#Installing GDAL

apt-get update
apt-get install -y g++ libgdal-dev gdal-bin=2.1.2+dfsg-5+deb9u1

export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

pip install gdal==2.1.3

#Install modified OpenCV

apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg

#chmod +x install_gdal_and_openCV.sh && ./install_gdal_and_openCV.sh && gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app