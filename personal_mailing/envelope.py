from email.message import EmailMessage
from person import Person

class Envelope:
    def __init__(self, msg: EmailMessage, to: Person) -> None:
        self.msg = msg
        self.to = to
