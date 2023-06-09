from email.utils import formataddr


class Emailable:
    def __init__(self, email_address:str, name:str='') -> None:
        self.email_address = email_address
        self.name = name

    @property
    def email_header_name(self) -> str:
        return formataddr((self.name, self.email_address))


class Person(Emailable):
    def __init__(self, first_name:str, last_name:str, email_address:str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        super().__init__(email_address, f"{self.first_name} {self.last_name}")

    # @property
    # def full_name(self) -> str:
    #     return f"{self.first_name} {self.last_name}"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.email_address})"
