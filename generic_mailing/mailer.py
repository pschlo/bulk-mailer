from __future__ import annotations
import smtplib, ssl
from email.message import EmailMessage
from person import Person
from collections.abc import Collection, Iterable
import logging
from typing import Any, TYPE_CHECKING
import time
from .envelope import Envelope
from .result import SendResult
from .types import SendErrs, SendSuccs
from mail_utils import ask_mail_confirmation


log = logging.getLogger()

COMMASPACE = ', '


class SMTP_CONFIG:
    def __init__(self,
                 address: str,
                 port: int,
                 ssl: bool = True,
                 username: str|None = None,
                 password: str|None = None
                 ) -> None:
        self.address = address
        self.port = port
        self.ssl = ssl
        self.username = username
        self.password = password


class SendCancelled(Exception):
    pass

class IncompleteLoginError(Exception):
    pass



# works with 'with' statement

class Mailer:
    sender: Person
    confirm_send: bool
    server: smtplib.SMTP
    last_send: float = 0
    delay_secs: float

    def __init__(self, config: SMTP_CONFIG, sender: Person, confirm_send:bool=False, delay_secs:float=0, detailed_log:bool=True) -> None:
        self.sender = sender
        self.confirm_send = confirm_send
        self.delay_secs = delay_secs
        self.detailed_log = detailed_log

        if config.ssl:
            log.debug("Connecting to SMTP server securely (SSL on)")
            context = ssl.create_default_context()
            self.server = smtplib.SMTP_SSL(config.address, config.port, context=context)
        else:
            log.debug("Connecting to SMTP server insecurely (SSL off)")
            self.server = smtplib.SMTP(config.address, config.port)

        if config.username is not None and config.password is None:
            raise IncompleteLoginError("User provided but password missing")
        if config.password is not None and config.username is None:
            raise IncompleteLoginError("Password provided but user missing")
        if config.username is not None and config.password is not None:
            log.debug(f"Logging in: '{config.username}'@{config.address}:{config.port}")
            self.server.login(config.username, config.password)
        else:
            log.debug("Skipping login")

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, tb: Any):
        log.debug("Disconnecting from SMTP server")
        self.server.__exit__(exc_type, exc_value, tb)
    
    def quit(self):
        log.debug("Disconnecting from SMTP server")
        self.server.quit()

    def wait(self):
        wait_for_secs = self.delay_secs - (time.monotonic() - self.last_send)
        if wait_for_secs > 0:
            log.debug(f"Waiting for {round(wait_for_secs, 2)} seconds")
            time.sleep(wait_for_secs)


    # returns tuple (succeeded, failed)
    def send_mail(self,
             msg: EmailMessage,
             to: Person | Collection[Person],
             cc: Person | Collection[Person] | None = None,
             bcc: Person | Collection[Person] | None = None,
             confirm: bool | None = None
             ) -> tuple[SendSuccs, SendErrs]:
        
        log = logging.getLogger('send_mail')

        env = Envelope(msg, to, cc, bcc)
        del to, cc, bcc
    
        if confirm is None:
            confirm = self.confirm_send

        msg["From"] = self.sender.email_header_name
        msg["To"] = COMMASPACE.join(r.email_header_name for r in env.to)
        if env.cc:
            msg["Cc"] = COMMASPACE.join(r.email_header_name for r in env.cc)

        from_addr = self.sender.email_address
        # ensure that every person is addressed at most once (i.e. remove duplicates), but preserve order
        to_people = list(dict.fromkeys(r for r in env.all_recipients))

        # disallow sending to same address multiple times
        # when same recipient is specified multiple times, email gets also send multiple times, but there will be max. 1 error entry
        # if e.g. the address was accepted the first time but rejected the second time, we cannot know if the address got the email 0 or 1 time.
        to_addrs = list({r.email_address for r in to_people})

        if confirm:
            log.debug("Awaiting e-mail confirmation")
            if not ask_mail_confirmation(env, "Send", "Cancel"):
                log.debug(f"E-mail cancelled")
                raise SendCancelled()

        self.wait()

        try:
            log.debug("Sending e-mail")
            self.last_send = time.monotonic()
            failed_addrs = self.server.send_message(msg, from_addr, to_addrs)
        except smtplib.SMTPRecipientsRefused as e:
            failed_addrs = e.recipients


        # convert failed_addrs to people
        failed: SendErrs = dict()
        for addr, error in failed_addrs.items():
            people = [p for p in to_people if p.email_address == addr]
            for person in people:
                failed[person] = error

        succeeded: SendSuccs = set(to_people) - set(failed)


        if not succeeded:
            log.error(f"E-mail sent: rejected for every recipient")
        elif failed:
            log.warning(f"E-mail sent: accepted by {len(succeeded)} of {len(to_people)} recipients")
        else:
            log.info(f"E-mail sent: accepted for every recipient")

        if self.detailed_log or log.isEnabledFor(logging.DEBUG):
            for recipient in succeeded:
                log.info(f"   ACCEPTED:  {recipient}")
            for recipient, error in failed.items():
                log.error(f"   REJECTED:  {recipient} (code {error[0]}): {error[1].decode()}")

        return succeeded, failed


    def send_queue_iter(self, queue: Collection[Envelope]) -> Iterable[SendResult]:
        for env in queue:
            cancelled = False
            succeeded: SendSuccs
            failed: SendErrs
            try:
                succeeded, failed = self.send_mail(env.msg, env.to, env.cc, env.bcc)
            except SendCancelled:
                cancelled = True
                succeeded = set()
                failed = dict()
            result = SendResult(env, succeeded, failed, cancelled)
            yield result


    def send_queue(self, queue: Collection[Envelope]) -> None:
        log.info(f"Sending {len(queue)} queued e-mails")
        for _ in self.send_queue_iter(queue):
            pass
        log.info(f"Sending queue finished")


    

