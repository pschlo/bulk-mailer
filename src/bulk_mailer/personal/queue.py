from collections.abc import Collection
from typing import Any, TypeVar, Callable
from .envelope import Envelope
from email.message import EmailMessage
from bulk_mailer.entities import Person
import logging


log = logging.getLogger()

_RecipientType = TypeVar('_RecipientType', bound=Person)


class MailQueue(Collection[Envelope]):
    def __init__(self, confirm_mails: bool = False, detailed_log: bool = True) -> None:
        self.queue = MailQueue(confirm_mails)
        self.detailed_log = detailed_log

    def __contains__(self, item: Any):
        return item in self.queue

    def __iter__(self):
        yield from self.queue

    def __len__(self):
        return len(self.queue)

    def add(self, msg: EmailMessage, to: Person) -> bool:
        return self.queue.add(msg, to)
    
    def add_for(self, recipients: Collection[_RecipientType], get_mail: Callable[[_RecipientType], EmailMessage]):
        log.info(f"Adding {len(recipients)} e-mails to queue")

        cancelled: set[_RecipientType] = set()
        for r in recipients:
            mail = get_mail(r)
            is_accepted = self.add(mail, r)
            if not is_accepted:
                cancelled.add(r)
        accepted: set[_RecipientType] = set(recipients) - cancelled

        if not accepted:
            log.error(f"No e-mails have been added to the queue")
        elif cancelled:
            log.warning(f"{len(accepted)} of {len(recipients)} e-mails have been added to queue")
        else:
            log.info(f"All e-mails have been added to the queue")

        if self.detailed_log or log.isEnabledFor(logging.DEBUG):
            for recipient in accepted:
                log.info(f"   ACCEPTED:  {recipient}")
            for recipient in cancelled:
                log.warning(f"   CANCELLED:  {recipient}")
