from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, re


def SendEmail(receiver, title, content):
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
    mail_title = title
    message['Subject'] = Header(mail_title, 'utf-8')

    # Content of the Email
    message.attach(MIMEText(content, 'plain', 'utf-8'))

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
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex,email):  
        return 1
    return 0