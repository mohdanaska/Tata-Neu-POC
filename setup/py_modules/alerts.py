from __future__ import print_function
import sys
import requests
import smtplib
if sys.version_info[0] < 3:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEImage import MIMEImage

else:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
import socket
import json

class SendAlert:
    def email_alert(self, subject, message_to_be_send, screenshot_attachment=None):
        message = message_to_be_send
        msg = MIMEMultipart()
        msg["Subject"] = subject

        msg.attach(MIMEText(message))
        recepients = ["megha@headspin.io","namrata@headspin.io","hemant.rathore@verse.in","abhilash.somanchi@verse.in","shailendra.sharma@verse.in","shrikant.kadu@verse.in","shahbaz.hasan@verse.in"]
        update_recepients=["megha@headspin.io","namrata@headspin.io"]
        server = smtplib.SMTP('smtp.gmail.com:587')
        if screenshot_attachment !=None:
            msg.attach(MIMEImage(open(screenshot_attachment,'rb').read()))
        server.starttls()
        server.login("hs_test2@hspin.io", "head$p!n@123")
        if subject=="APP_UPDATE":
            server.sendmail("hs_test2@hspin.io", update_recepients, msg.as_string())
            print("only megha and namrata")

        else:
            server.sendmail("hs_test2@hspin.io", recepients, msg.as_string())
            print("everyone")
        
    @staticmethod
    def slack_alert(message_to_be_send):
        '''
        Sample for the params dic
        params = {'channel': "#globo_alerts", 'username':'webhookbot', 'text': "<message_to_be_sent>,"icon_emoji": ':ghost:'}
        '''
        message = socket.gethostname()+"\n"+message_to_be_send
        url = "https://hooks.slack.com/services/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"
        params = {'text': "%s" % message}
        r= requests.post(url=url, data=json.dumps(params))
        print(r.text)
