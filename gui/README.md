# Environment
The environment is based on Python3
1. Install PyQt4.
QT no longer supports PyQt4
For windows, you can find the .whl file from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4 and download it. Then run the following command to install PyQt4.
```
pip install PyQt4‑4.11.4‑cp36‑cp36m‑win_amd64.whl
```
For Ubuntu, you can build PyQt4 from sources (https://riverbankcomputing.com/software/pyqt/download) with sip installed.
```
wget https://www.riverbankcomputing.com/static/Downloads/PyQt4/4.12.3/PyQt4_gpl_x11-4.12.3.tar.gz
tar -zxvf PyQt4_gpl_x11-4.12.3.tar.gz
cd PyQt4_gpl_x11-4.12.3
python configure-ng.py
make
make  install
```
2. Install other package
```
conda install -c menpo opencv
conda install -c menpo dliib
pip install qimage2ndarray
pip install scikit-image
pip install moviepy
```
# Usage

Run the run.py under the gui direction.

```
python run.py
```