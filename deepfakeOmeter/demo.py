import flask

from flask import  render_template, url_for, redirect, request

from flask import Flask
app = Flask(__name__)


@app.route('/reference')
def index():
    return render_template('reference.html')


@app.route("/", methods=['POST', 'GET'])
def hello_world():

    data = []
    videohtml = ''
    methodhtml = ''

    # render_template('select.html')
    if request.method == 'POST':
        methods = request.values.getlist("method")
        videos = request.values.getlist("video")
        for method in methods:
            for video in videos:
                data.append({'name':video+method+' 00_00_00-00_00_30.gif', 'note': 'Analysis the %s with the DeepFake Detection method %s' %(video[:-1]+'.mp4', method),
                             'jpg':video+method+'.jpg'})
        print(methods, videos)
        print(methods)
        for datas in data:
            print(datas['name'])
        for method in methods:
            if methodhtml:
                methodhtml += ', '
            methodhtml +=  method


        for video in videos:
            if videohtml:
                videohtml += ', '
            videohtml +=  video+'.mp4'
        return render_template('deepfakeOmeter.html', datas=data, methods=methodhtml, videos=videohtml)

    return render_template('deepfakeOmeter_index.html', datas=data, methods=methodhtml, videos=videohtml)



app.run(host='0.0.0.0', port=5000, debug=True)
