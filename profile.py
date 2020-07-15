from quote import Quote
from address import Address

class Profile:
    def __init__(self, username, name, address, quotes=[]):
        self.name = name
        self.username = username
        self.quotes = quotes
        self.address = address
        self.quoteinprogress = None
    def __eq__(self, other):
        if(isinstance(other, Profile) and self.username == other.username and self.name == other.name and self.address == other.address):
            for (quote, otherquote) in zip(self.quotes, other.quotes):
                if(not (quote == otherquote)):
                    return False
            return True