class Quote:
    def __init__(self, gallons, date, price, total, address=""):
        self.gallons = gallons
        self.date = date
        self.price = price
        self.total = total
        self.address = address
    def __repr__(self):
        return str(self.gallons) + "\n" + str(self.date) + "\n" + str(self.price) + "\n" + str(self.total) + "\n" + str(self.address) + "\n"
    def __eq__(self, other):
    	return isinstance(other, Quote) and self.gallons == other.gallons and self.date == other.date and self.price == other.price and self.total == other.total and self.address == other.address