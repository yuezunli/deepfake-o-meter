import flask

from flask import  render_template, url_for, redirect, request

from flask import Flask
app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def hello_world():
    methods = []
    videos = []
    data = []

    # render_template('select.html')
    if request.method == 'POST':
        methods = request.values.getlist("method")
        videos = request.values.getlist("video")
        for method in methods:
            for video in videos:
                data.append({'name':video+method+' 00_00_00-00_00_30.gif', 'note': 'Analysis the %s with the DeepFake Detection method %s' %(video[:-1]+'.mp4', method)})
        print(methods, videos)
        print(methods)
    for datas in data:
        print(datas['name'])

    return render_template('select.html', datas=data)



app.run(host='0.0.0.0', debug=True)