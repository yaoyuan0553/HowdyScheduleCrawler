import smtplib

class EmailReminder(object):

    sentFrom = "0553yaoyuan@gmail.com"
    to = ["0553yaoyuan@gmail.com", "0553yaoyuan@gmail.com"]
    subject = "Class Ready"
    body = "Check Howdy"

    emailText = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sentFrom, ", ".join(to), subject, body)

    def sendEmail(self):
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login("0553yaoyuan@gmail.com", "09Gefei20-14")

        server.sendmail(sentFrom, to, emailText)
        server.close()
        
        print "email sent"


emailReminder = EmailReminder()