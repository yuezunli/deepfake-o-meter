import sys, os
sys.path.append("..")
import pickle, cv2
import deepfor, os
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
model = deepfor.CapsuleNet()

@app.route('/deepforensics', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force = True)
    res = model.run(np.array(data['feature']).astype(np.uint8))
    res = [res]
    return jsonify(str(res))


if __name__ == '__main__':
    # os.environ["CUDA_VISIBLE_DEVICES"]= '1'
    app.run(debug = True, host = '0.0.0.0', port='5006')
