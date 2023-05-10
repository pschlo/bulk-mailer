from __future__ import annotations
from email.message import EmailMessage
from person import Person
from collections.abc import Collection
from typing import TYPE_CHECKING, Any
from mail_utils import ask_mail_confirmation
import logging
from generic_mailing.envelope import Envelope


log = logging.getLogger()


class MailQueue(Collection[Envelope]):

    def __init__(self, confirm_mails:bool=False) -> None:
        self.queue: list[Envelope] = []
        self.confirm_mails = confirm_mails
    
    def __contains__(self, item: Any):
        return item in self.queue

    def __iter__(self):
        yield from self.queue

    def __len__(self):
        return len(self.queue)
    
    def __str__(self) -> str:
        return str(self.queue)

    def add(self,
            msg: EmailMessage,
            to: Person | Collection[Person],
            cc: Person | Collection[Person] | None = None,
            bcc: Person | Collection[Person] | None = None
            ) -> bool:

        envelope = Envelope(msg, to, cc, bcc)
        if self.confirm_mails and not ask_mail_confirmation(envelope, "Accept", "Reject"):
            log.debug("Mail rejected")
            return False
        self.queue.append(envelope)
        return True
