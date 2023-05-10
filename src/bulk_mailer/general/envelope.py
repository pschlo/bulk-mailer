from email.message import EmailMessage
from collections.abc import Collection
from bulk_mailer.entities import Emailable
from itertools import chain


"""
This class serves as a wrapper around an e-mail.
It can be used if sending the e-mail should be done at a later point in time.
"""

class Envelope:
    def __init__(self, 
                 msg: EmailMessage,
                 to: Emailable | Collection[Emailable],
                 cc: Emailable | Collection[Emailable] | None = None,
                 bcc: Emailable | Collection[Emailable] | None = None
                 ) -> None:
        
        if cc is None:
            cc = []
        if bcc is None:
            bcc = []

        if isinstance(to, Emailable):
            to = [to]
        if isinstance(cc, Emailable):
            cc = [cc]
        if isinstance(bcc, Emailable):
            bcc = [bcc]

        self.msg: EmailMessage = msg
        self.to: Collection[Emailable] = to
        self.cc: Collection[Emailable] = cc
        self.bcc: Collection[Emailable] = bcc
    
    @property
    def all_recipients(self):
        return chain(self.to, self.cc, self.bcc)