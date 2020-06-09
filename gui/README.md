# Environment
The environment is based on Python3. The framework is pyqt4 or pyqt5.


## Install PyQt4.

### windows
you can find the .whl file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4 and download it. Then run the following command to install PyQt4.

```
pip install PyQt4‑4.11.4‑cp36‑cp36m‑win_amd64.whl
```

### Ubuntu

```
sudo apt-get install python3-pyqt4
```
or you can build PyQt4 from sources (https://riverbankcomputing.com/software/pyqt/download) with sip installed.
```
wget https://www.riverbankcomputing.com/static/Downloads/PyQt4/4.12.3/PyQt4_gpl_x11-4.12.3.tar.gz
tar -zxvf PyQt4_gpl_x11-4.12.3.tar.gz
cd PyQt4_gpl_x11-4.12.3
python configure-ng.py
make
make  install
```

Note QT no longer supports PyQt4

## Install PyQt5

### Ubuntu 18.04
```
pip install pyqt5==5.14.0
```

## Other packages
```
pip install opencv-python3 dlib qimage2ndarray scikit-image moviepy

```
# Usage

Run the run.py under the gui direction.

```
python run.py
```