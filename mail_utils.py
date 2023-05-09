from __future__ import annotations
from email.message import EmailMessage
from pathlib import PurePath
from collections.abc import Collection
from mimetypes import guess_type
try:
    from confirm_mail_interactive import ask_send_confirmation as _ask_send_confirmation
except ModuleNotFoundError:
    from confirm_mail_stdout import ask_send_confirmation as _ask_send_confirmation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from generic_mailing.mailer import Envelope



def ask_mail_confirmation(envelope: Envelope, accept:str="Accept", reject:str="Reject"):
    text = mail_to_str(envelope)
    return _ask_send_confirmation(text, accept, reject)


def mail_to_str(envelope: Envelope) -> str:
    msg = envelope.msg
    text = ""

    text += "--- RECIPIENTS ---\n"
    text += f"To: {', '.join(p.email_header_name for p in envelope.to)}\n"
    text += f"Cc: {', '.join(p.email_header_name for p in envelope.cc)}\n"
    text += f"Bcc: {', '.join(p.email_header_name for p in envelope.bcc)}\n"
    text += "\n\n"

    text += "--- ATTACHMENTS ---\n"
    for a in msg.iter_attachments():
        assert isinstance(a, EmailMessage)
        text += f"{a.get_filename()} ({a.get_content_type()})\n"
    text += "\n\n"

    headers = msg.items()
    text += "--- HEADER ---\n"
    for header in headers:
        text += f"{header[0]}: {header[1]}\n"
    text += "\n\n"

    body = msg.get_body()
    assert isinstance(body, EmailMessage)
    text += "--- BODY ---\n"
    text += body.get_content()

    return text


def create_plain_mail(subject: str, body: str, attachments: PurePath | Collection[PurePath] | None = None) -> EmailMessage:
    if attachments is None:
        attachments = []

    if not isinstance(attachments, Collection):
        attachments = [attachments]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg.set_content(body, subtype='plain')

    for attachment in attachments:
        with open(attachment, 'rb') as f:
            data = f.read()

        mime_type = guess_type(attachment, strict=False)[0]
        if mime_type is None:
            mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split('/')
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=attachment.name)

    return msg