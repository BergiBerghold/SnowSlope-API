Um OpenCV selber zu compilieren hab i die Anleitung befolgt: https://docs.opencv.org/4.x/d7/d9f/tutorial_linux_install.html

Im Sourcecode hab i an der Datei opencv/modules/imgproc/src/floodfill.cpp ummapfuscht und dann alles compiliert.

Wenn dann des ganze compiliert is muast die Datei "cv2.cpython-38-x86_64-linux-gnu.so" in "/usr/lib/python3/dist-packages"
und "/usr/local/lib/python3.6/dist-packages/cv2" ersetzen mit "./lib/python3/cv2.cpython-38-x86_64-linux-gnu.so" aus deim
Build. I hab OpenCV 4.2.0 und i hob die von mit compilierte ".so" Datei im "OpenCV Custom Build" Ordner. Es is wahrscheinlich
wichtig dass du die gleichen OpenCV version hast sonst gibst vielleicht Probleme.

cmake -DBUILD_SHARED_LIBS=OFF -DBUILD_NEW_PYTHON_SUPPORT=ON -DBUILD_PYTHON_SUPPORT=ON -DPYTHON_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") -DPYTHON_LIBRARY=$(python -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))") ../opencv-source
