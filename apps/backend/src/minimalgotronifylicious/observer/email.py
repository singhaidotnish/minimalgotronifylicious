from .base_observer import BaseObserver

# Email Alert Observer
class EmailAlertObserver(BaseObserver):
    def send_email_alert(self, subject, body):
        sender = "your_email@gmail.com"
        receiver = "recipient_email@gmail.com"
        message = f"Subject: {subject}\n\n{body}"
        print(f"📧 [Email Alert] Sending email: {subject}")

        # Uncomment to send actual email (requires SMTP setup)
        # with smtplib.SMTP("smtp.example.com", 587) as server:
        #     server.starttls()
        #     server.login(sender, "your_password")
        #     server.sendmail(sender, receiver, message)

    def update(self, message):
        pass  # Not needed here since alerts are triggered from EMAObserver
