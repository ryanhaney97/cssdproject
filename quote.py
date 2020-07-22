class Quote:
    quote_by_id = {}
    def __init__(self, gallons, date, address, price=None):
        self.gallons = gallons
        self.date = date
        self.price = price
        self.address = address
        self.id = None
    def total(self):
        if(price is None):
            return None
        return self.price * self.gallons
    def setID(self, id):
        self.id = id
        Quote.quote_by_id[id] = self
    def __repr__(self):
        return f"{self.gallons}\n{self.date}\n{self.price}\n{self.address}\n"
    def __eq__(self, obj):
        return isinstance(obj, Quote) and self.gallons == obj.gallons and self.date == obj.date and self.price == obj.price and self.address == obj.address