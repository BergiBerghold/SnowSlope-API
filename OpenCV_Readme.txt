Um OpenCV selber zu compilieren hab i die Anleitung befolgt: https://docs.opencv.org/4.x/d7/d9f/tutorial_linux_install.html

Im Sourcecode hab i an der Datei opencv/modules/imgproc/src/floodfill.cpp ummapfuscht und dann alles compiliert.

Wenn dann des ganze compiliert is muast die Datei "cv2.cpython-38-x86_64-linux-gnu.so" in "/usr/lib/python3/dist-packages"
und "/usr/local/lib/python3.6/dist-packages/cv2" ersetzen mit "./lib/python3/cv2.cpython-38-x86_64-linux-gnu.so" aus deim
Build. I hab OpenCV 4.2.0 und i hob die von mit compilierte ".so" Datei im "OpenCV Custom Build" Ordner. Es is wahrscheinlich
wichtig dass du die gleichen OpenCV version hast sonst gibst vielleicht Probleme.

