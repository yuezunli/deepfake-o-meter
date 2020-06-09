import sys, os
sys.path.append(os.path.dirname(__file__) + '/../')
import pickle, cv2, deepfor
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
model = deepfor.DSPFWA()

@app.route('/deepforensics', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force = True)
    rois, loc = model.crop_face(np.array(data['feature']).astype(np.uint8))
    conf = model.get_softlabel(rois)
    res = [loc, conf]
    # conf = 0
    return jsonify(str(res))


if __name__ == '__main__':
    app.run(debug = False, host = '0.0.0.0')
