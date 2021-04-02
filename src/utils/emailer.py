import smtplib
from email.mime.text import MIMEText
from decouple import config
import yagmail

# # Open a plain text file for reading.  For this example, assume that
# # the text file contains only ASCII characters.
# with open(textfile, 'rb') as fp:
#     # Create a text/plain message
#     msg = MIMEText(fp.read())

# # me == the sender's email address
# # you == the recipient's email address
# msg['Subject'] = 'The contents of %s' % textfile
# msg['From'] = me
# msg['To'] = you

# # Send the message via our own SMTP server, but don't include the
# # envelope header.
# s = smtplib.SMTP('localhost')
# s.sendmail(me, [you], msg.as_string())
# s.quit()

# contents = [
#     "This is the body, and here is just text http://somedomain/image.png",
#     "You can find an audio file attached.", '/local/path/to/song.mp3'
# ]
# yag.send('to@someone.com', 'subject', contents)

# # Alternatively, with a simple one-liner:
# yagmail.SMTP('mygmailusername').send('to@someone.com', 'subject', contents)

class Emailer():

    def __init__(self):
        # import ipdb; ipdb.set_trace()
        # self.s = smtplib.SMTP('localhost')
        # smtplib.SMTP.starttls()
        # self.s = smtplib.SMTP('smtp.gmail.com')
        self.sender_email = config("EMAIL_USERNAME")
        self.yag = yagmail.SMTP(self.sender_email, config('EMAIL_PWD'))

    def send_email(self, reciever_email, contents, subject):
        # msg = MIMEText(message)
        # msg['Subject'] = message
        # msg['From'] = sender
        # msg['To'] = reciever
        # self.s.sendmail(sender, [reciever], msg.as_string())
        self.yag.send(reciever_email, subject, contents)
        




if __name__ == "__main__":
    emailer = Emailer()
    emailer.send_email("brydonparker4@gmail.com", "test", "test")
