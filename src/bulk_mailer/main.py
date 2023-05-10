from person import Person
from personal_mailing.mailer import Mailer, SMTP_CONFIG
from mail_utils import create_plain_mail
from getpass import getpass


def main():
    p1 = Person('', '', 'abc@gmail.com')

    config = SMTP_CONFIG(
        '',
        465,
        ssl = True,
        username = '',
        password = getpass()
    )

    with Mailer(config, sender=p1) as mailer:
        mail = create_plain_mail('Hello', 'This is a test!')
        mailer.send_mail(mail, p1)


if __name__ == "__main__":
    # main()

    import playground
    playground.main()