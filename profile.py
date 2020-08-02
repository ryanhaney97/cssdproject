from quote import Quote
from address import Address

class Profile:
    def __init__(self, username, name, address, quotes=[]):
        self.name = name
        self.username = username
        self.quotes = quotes
        self.address = address
        self.quoteinprogress = None
    @staticmethod
    def from_str(profilestr):
        username, name, *addrstr = quotestr.split("|")
        address = Address(*addrstr)
        return Profile(username, name, address)
    def __eq__(self, other):
        if(isinstance(other, Profile) and self.username == other.username and self.name == other.name and self.address == other.address):
            for (quote, otherquote) in zip(self.quotes, other.quotes):
                if(not (quote == otherquote)):
                    return False
            return True
    def __str__(self):
        return f"{self.username}|{self.name}|{self.address}"