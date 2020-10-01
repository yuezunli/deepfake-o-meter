
activate_this = '/web/ubmdfl/deepfake-o-meter/venv-dfom/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0,"/web/ubmdfl/deepfake-o-meter/web")

from run import app as application
