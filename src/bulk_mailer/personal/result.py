from .envelope import Envelope
from .types import Error


class SendResult:
    def __init__(self, envelope: Envelope, error: Error, cancelled: bool) -> None:
        self.envelope = envelope
        self.error = error
        self.cancelled = cancelled
