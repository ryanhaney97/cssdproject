class Quote:
    def __init__(self, gallons, date, price, total):
        self.gallons = gallons
        self.date = date
        self.price = price
        self.total = total
        for x in range(0,100):
            self.address[x] = ' '

    def getGal(self):
        return self.gallons

    def getAdd(self):
        return self.address

    def getDate(self):
        return self.date

    def getPrice(self):
        return self.price

    def getTotal(self):
        return self.total

    def setGal(self, gal):
        self.gallons = gal

    def setAdd(self, add):
        for x in range(0,100):
            self.address[x] = add

    def setDate(self, dat):
        self.date = dat

    def setPrice(self, pri):
        self.price = pri

    def setTotal(self, tot):
        self.total = tot
