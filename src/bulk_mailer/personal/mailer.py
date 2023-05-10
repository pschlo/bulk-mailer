from collections.abc import Collection
from email.message import EmailMessage
from bulk_mailer.general.mailer import SMTP_CONFIG, Mailer as GenericMailer, SendCancelled
from bulk_mailer.entities import Emailable
from typing import Any
import logging
from .queue import MailQueue
from .result import SendResult
from .types import Error


log = logging.getLogger()



class Mailer:
    def __init__(self, config: SMTP_CONFIG, sender: Emailable, confirm_send: bool = False, delay_secs: float = 0, detailed_log: bool = True) -> None:
        self.mailer = GenericMailer(config, sender, confirm_send, delay_secs=delay_secs, detailed_log=detailed_log)
        self.detailed_log = detailed_log

    def __enter__(self):
        self.mailer.__enter__()
        return self
    
    def __exit__(self, *args: Any):
        self.mailer.__exit__(*args)

    # returns reply if error
    # returns None if success
    def send_mail(self, msg: EmailMessage, to: Emailable) -> Error:
        _, failed = self.mailer.send_mail(msg, to)
        return next(iter(failed.values())) if failed else None

    def send_queue_iter(self, queue: MailQueue):
        for env in queue:
            cancelled = False
            try:
                error = self.send_mail(env.msg, env.to)
            except SendCancelled:
                cancelled = True
                error = None
            result = SendResult(env, error, cancelled)
            yield result
    
    def send_queue(self, queue: MailQueue) -> tuple[Collection[Emailable], Collection[Emailable], Collection[Emailable]]:
        succeeded: set[Emailable] = set()
        failed: set[Emailable] = set()
        cancelled: set[Emailable] = set()

        log.info(f"Sending {len(queue)} queued personal e-mails")

        for res in self.send_queue_iter(queue):
            to = res.envelope.to
            if res.cancelled:
                cancelled.add(to)
            elif res.error:
                failed.add(to)
            else:
                succeeded.add(to)

        if succeeded:
            if failed:
                level = logging.WARNING
            else:
                level = logging.INFO if not cancelled else logging.WARNING
        else:
            level = logging.ERROR

        log.log(level, f"Sending queue finished ({len(succeeded)} successful, {len(failed)} failed, {len(cancelled)} cancelled)")
        if self.detailed_log or log.isEnabledFor(logging.DEBUG):
            for recipient in succeeded:
                log.info(f"   SUCCEEDED:  {recipient}")
            for recipient in failed:
                log.error(f"   FAILED:  {recipient}")
            for recipient in cancelled:
                log.warning(f"   CANCELLED:  {recipient}")

        return succeeded, failed, cancelled

