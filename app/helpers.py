from django.core.mail import send_mail
from raffle.settings import DEFAULT_FROM_EMAIL
import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, message, html_message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run (self):
        send_mail(subject=self.subject,
                  message=self.message,
                  html_message=self.html_message,
                  from_email=DEFAULT_FROM_EMAIL,
                  recipient_list=self.recipient_list)

def sendEmailLoser(user):
    plain_message = "You didn't win the raffle."
    html_message = "You didn't win the raffle."
    EmailThread(subject="Didn't won",
                  message=plain_message,
                  html_message=html_message,
                  recipient_list=[user.email]).start()

def sendEmailWinner(user, name, amount):
    plain_message = "You won the <b> name <b> raffle. The prize is " + str(amount)
    html_message  = "You won the <b> name <b> raffle. The prize is " + str(amount)
    EmailThread(subject="You won!",
                message=plain_message,
                html_message=html_message,
                recipient_list=[user.email]).start()