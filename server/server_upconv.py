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
    data = request.get_json(force=True)
    cropped_face, loc = model.crop_face(np.array(data['feature']).astype(np.uint8))
    if len(cropped_face):
        preproced_face = model.preproc(cropped_face)
        conf = model.get_softlabel(preproced_face)
    else:
        conf = 0.5
    loc.append(conf)
    return jsonify(str(loc))


if __name__ == '__main__':

    app.run(debug = True, host = '0.0.0.0', port = '5001')
