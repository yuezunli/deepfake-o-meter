import sys, os
sys.path.append("..")
import pickle, cv2
import deepfor
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
model = deepfor.SelimSeferbekov()

@app.route('/deepforensics', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force = True)
    rois, loc = model.crop_face(np.array(data['feature']).astype(np.uint8))
    conf = model.get_softlabel(rois)
    res = [loc[0], loc[1], loc[2], loc[3], conf]

    return jsonify(str(res))


if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"]='1'
    app.run(debug = True, host = '0.0.0.0', port='5004')
