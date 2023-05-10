from email.message import EmailMessage
from collections.abc import Collection
from person import Emailable
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

        if not isinstance(to, Collection):
            to = [to]
        if not isinstance(cc, Collection):
            cc = [cc]
        if not isinstance(bcc, Collection):
            bcc = [bcc]

        self.msg: EmailMessage = msg
        self.to: Collection[Emailable] = to
        self.cc: Collection[Emailable] = cc
        self.bcc: Collection[Emailable] = bcc
    
    @property
    def all_recipients(self):
        return chain(self.to, self.cc, self.bcc)