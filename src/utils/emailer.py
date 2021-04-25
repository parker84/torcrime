from decouple import config
import yagmail

class Emailer():

    def __init__(self):
        self.sender_email = config("EMAIL_USERNAME")
        self.yag = yagmail.SMTP(self.sender_email, config('EMAIL_PWD'))

    def send_email(self, reciever_email, contents, subject):
        self.yag.send(reciever_email, subject, contents)

if __name__ == "__main__":
    emailer = Emailer()
    emailer.send_email("brydonparker4@gmail.com", "test", "test")
