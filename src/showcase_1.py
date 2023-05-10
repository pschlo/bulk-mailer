
from getpass import getpass
from bulk_mailer.personal import Mailer, SMTP_CONFIG
from bulk_mailer.utils import create_plain_mail
from bulk_mailer.entities import Emailable


def main():
    name = input("Name: ")
    email_address = input("E-mail address: ")
    person = Emailable(email_address, name)

    config = SMTP_CONFIG(
        address = input("SMTP address: "),
        port = 465,
        ssl = True,
        username = input("SMTP username: "),
        password = getpass("SMTP password: ")
    )

    with Mailer(config, sender=person) as mailer:
        mail = create_plain_mail('Hello', 'This is a test!')
        mailer.send_mail(mail, person)


if __name__ == "__main__":
    main()
