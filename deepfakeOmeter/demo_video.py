import flask, os, time, re, time, you_get, sys, shutil, smtplib, argparse, time
import numpy as np
from datetime import datetime
from flask import  render_template, url_for, redirect, request, Flask
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def SendEmail(receiver, pin):
    """
    Send the email to inform the user, we have received his submission.
    :param receiver: the receiver's email address
    :param pin: the pin code the receiver submit
    """
    # Information about the email sender
    sender = 'zchh1209@163.com'
    smtpserver = 'smtp.163.com'
    username = 'zchh1209'
    password = 'UFLRRRLDPWZKJDWV'

    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver

    # Title of the Email
    mail_title = 'DeepFakeOmeter got your submission'
    message['Subject'] = Header(mail_title, 'utf-8')

    # Content of the Email
    message.attach(MIMEText('We have received your submission. The result will be send to this email later.' + '\n' +
    'Please check your result and download them in 5 days.' + '\n' +
    'Please remeber your pin code:' + pin + '\n' +
    'If you don not  get the results in 5 days, Pleasse contact us.'
    , 'plain', 'utf-8'))

    smtpObj = smtplib.SMTP_SSL(smtpserver)
    smtpObj.connect(smtpserver)
    smtpObj.login(username, password)
    smtpObj.sendmail(sender, receiver, message.as_string())
    print("suceed")
    smtpObj.quit()


def validateEmail(email):
    """
    Check the email if it is valid
    :param email: the email provided by th user
    :return: 1 for right, 0 for wrong
    """
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0


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
            basepath = os.path.dirname(__file__)
            emailDir = os.path.join(basepath, 'tmp', email)
            dataDir = os.path.join(basepath, 'tmp', email, timerecord)
            if not os.path.isdir(emailDir):
                os.mkdir(emailDir)
            if not os.path.isdir(dataDir):
                os.mkdir(dataDir)
            upload_path = os.path.join(basepath, 'tmp', email, timerecord)
            # save the video and pin code
            np.save(upload_path+'/methods', methods)
            np.save(upload_path+'/pin', pin)
            if f.filename:
                f.save("tmp.mp4")
                shutil.move("tmp.mp4",os.path.join(upload_path, f.filename))
            else:
                sys.argv = ['you-get', '-o', upload_path, '-O', 'tmp', fileurl]
                you_get.main()

            with open(os.path.join(upload_path, (f.filename).split('.')[0]+'.csv'), 'w') as f:
                f.writelines('Finish Save!')
            # send the email
            SendEmail(email, pin)
        return render_template('succeed.html')


@app.route('/error/<string:type>')
def error(type):
    if type=='Email':
        error = 'email address'
    elif type=='Input':
        error = 'input video'
    elif type=='Method':
        error = 'selected methods'
    return render_template('error.html', error=error, type=type)


#the reference website
@app.route('/reference')
def index():
    return render_template('reference.html')

app.run(host='0.0.0.0', debug=True, port=5006)
