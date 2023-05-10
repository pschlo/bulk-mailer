from email.message import EmailMessage
from person import Emailable

class Envelope:
    def __init__(self, msg: EmailMessage, to: Emailable) -> None:
        self.msg = msg
        self.to = to
