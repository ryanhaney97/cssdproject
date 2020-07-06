from quote import Quote

class Profile:
    def __init__(self, username, password, name, city, state, zipcode, address1, address2=""):
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.username = username
        self.password = password
        self.quotes = []

    def Registered(self, user):
        return user == self.username

    def Login(self, user, password):
        return self.username == user and self.password == password

    def QuoteHistory(self):
        for quote in self.quotes:
            print(quote)

    def addQuote(self, gallons, date, price, total, address=""):
        self.quotes.append(Quote(gallons, date, price, total, address))
        
