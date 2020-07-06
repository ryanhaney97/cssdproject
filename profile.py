from quote import Quote

class Profile:
    def __init__(self, name, address1, address2 = "", city, state, zipcode, username, password):
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.username = username
        self.password = password
        self.quotes = Quote[]

    def Registered(self, user):
        bool found = false
        if user == self.username:
            found = true
        return found

    def Login(self, user, password):
        bool valid = false
        if self.username == user && self.password == password:
            valid = true
        return valid

    def QuoteHistory(self):
        i = 0
        while self.quotes:
            print(quotes[i].gallons, \n, quotes[i].address, \n, quotes[i].date, \n, quotes[i].price, \n, quotes[i].total)
            i++

    def addQuote(self, gallons, date, price, total, address=""):
        i = length(self.quotes)
        self.quotes[i] = Quote(gallons, date, price, total, address)
        
