from quote import Quote

class Profile:
    def __init__(self, username, password, name, city, state, zipcode, address1, address2="", quotes=[]):
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.username = username
        self.password = password
        self.quotes = quotes

    def Registered(self, user):
        return user == self.username

    def Login(self, user, password):
        return self.username == user and self.password == password

    def QuoteHistory(self):
        for quote in self.quotes:
            print(quote)

    def addQuote(self, gallons, date, price, total, address=""):
        self.quotes.append(Quote(gallons, date, price, total, address))
    def __eq__(self, other):
        return isinstance(other, Profile) and self.username == other.username and self.password == other.password and self.name == other.name and self.city == other.city and self.state == other.state and self.zipcode == other.zipcode and self.address1 == other.address1 and self.address2 == other.address2 and self.quotes == other.quotes
        
