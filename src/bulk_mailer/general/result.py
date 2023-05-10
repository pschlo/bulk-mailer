from .envelope import Envelope
from .types import SendSuccs, SendErrs



class SendResult:
    def __init__(self, envelope: Envelope, succeeded: SendSuccs, failed: SendErrs, cancelled: bool) -> None:
        assert cancelled or set(succeeded) | set(failed) == set(envelope.all_recipients)
        self.envelope = envelope
        self.succeeded = succeeded
        self.failed = failed
        self.cancelled = cancelled
        