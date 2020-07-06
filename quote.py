class Quote:
    def __init__(self, gallons, date, price, total, address=""):
        self.gallons = gallons
        self.date = date
        self.price = price
        self.total = total
        self.address = address
    def __repr__(self):
        return str(self.gallons) + "\n" + str(self.date) + "\n" + str(self.price) + "\n" + str(self.total) + "\n" + str(self.address) + "\n"