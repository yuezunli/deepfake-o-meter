import sys, os
# print(sys.path)
sys.path.append("..")
sys.path.append(os.path.dirname(__file__) + '/../')
# print(os.path.dirname(__file__))
import pickle, argparse, deepfor
# from .. deepfor import *
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--model', help='Model Name', default='LR_CelebA')
args = parser.parse_args()
# SVM_FacesHQ, LR_FacesHQ, SVM_FF, LR_FF, SVM_CelebA, SVM_r_CelebA, SVM_p_CelebA, LR_CelebA
model = deepfor.Upconv(mode =args.model)

@app.route('/deepforensics', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force = True)
    conf = model.run(np.array(data['feature']).astype(np.uint8)) # conf of fake
    return jsonify(conf[0].tolist())

if __name__ == '__main__':

    app.run(debug = True, host = '0.0.0.0')
