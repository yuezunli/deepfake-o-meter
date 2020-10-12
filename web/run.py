import flask, os, time, re, you_get, sys, shutil
import numpy as np
from datetime import datetime
from flask import  render_template, url_for, redirect, request, Flask, send_from_directory
#from email_utils import SendEmail, validateEmail


# Flask App
app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template('index.html')


#the submit website
@app.route('/submit', methods=['POST', 'GET'])
def submitpadge():
    if request.method == 'POST':
        # Get the submision information
        f = request.files['file']
        methods = request.values.getlist("method")
        email = request.values.getlist("input_email")[0]
        fileurl = request.values.getlist("input_file")[0]
        pin = request.values.getlist("input_pin")[0]
        timerecord = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        print('submit', methods, email)     

        # check if the submission information is right
        isEmail = validateEmail(email)
        if isEmail == 0:
            return redirect(url_for('error',type='Email'))
        elif not f.filename and len(fileurl)==0:
            return redirect(url_for('error',type='Input'))
        elif len(methods) == 0:
            return redirect(url_for('error',type='Method'))
        else:
            basepath = '/data/web/ubmdfl/deepfake-o-meter-sync-received/'  #os.path.dirname(__file__)
            # emailDir = os.path.join(basepath, 'tmp', email)
            upload_path = os.path.join(basepath, email, timerecord)
            #if not os.path.isdir(emailDir):
                #os.mkdir(emailDir)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            # upload_path = os.path.join(basepath, 'tmp', email, timerecord)
            
            # save the video and pin code
            np.save(upload_path+'/methods', methods)
            np.save(upload_path+'/pin', pin)
            if f.filename:
                f.save(os.path.join(upload_path, f.filename))
            else:
                sys.argv = ['you-get', '-o', upload_path, '-O', 'tmp', fileurl]
                you_get.main()

            with open(os.path.join(upload_path, (f.filename).split('.')[0]+'.csv'), 'w') as f:
                f.writelines('Finish Save!')
            # send the email
            title = 'DeepFake-o-meter received your submission'
            content = 'We have received your submission. The result will be send to your email later. \n' + \
            'Please remeber your pin code:' + pin + '\n' + \
            'If you don not receive the results in 2 days, Pleasse contact us via deepfake-o-meter@gmail.com.'
            SendEmail(email, title, content)
        return render_template('succeed.html')


@app.route('/error/<string:type>')
def error(type):
    if type=='Email':
        error = 'email address'
    elif type=='Input':
        error = 'input video'
    elif type=='Method':
        error = 'selected methods'
    elif type == 'Download URL':
        error = 'Download URL'
    return render_template('error.html', error=error, type=type)


#the reference website
@app.route('/reference')
def index():
    return render_template('reference.html')
    
    
    
# Downloading results    
@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # filename = email address _ PIN code _ date
    subfolders = filename.split('_')
    email = subfolders[0]
    pin = subfolders[1]
    date = subfolders[2]
    # Check if email and date are matched with PIN
    received_folder = '/data/web/ubmdfl/deepfake-o-meter-sync-received/{}/{}'.format(email, date)
    pin_ = np.load(os.path.join(received_folder, 'pin.npy'))
    if pin_ != pin:
        error('Download URL')

    directory = os.path.join('/data/web/ubmdfl/deepfake-o-meter-sync-result/{}/{}/'.format(email, date))
    fn = 'result.zip'
    if os.path.isfile(os.path.join(directory, fn)):
        return send_from_directory(directory, fn, as_attachment=True)
    raise exceptions.MyHttpNotFound('not found file')
    

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port=5006)
    app.run()
