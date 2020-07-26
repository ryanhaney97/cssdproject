from datetime import date as dtdate
from address import Address
class Quote:
    quote_by_id = {}
    def __init__(self, gallons, date, address, price=None):
        self.gallons = gallons
        self.date = date
        self.price = price
        self.address = address
        self.id = None
    @property
    def total(self):
        if(self.price is None):
            return None
        return self.price * self.gallons
    @property
    def id(self):
        return self.__id
    @id.setter
    def id(self, id):
        self.__id = id
        if(id is not None):
            Quote.quote_by_id[id] = self
    @staticmethod
    def from_str(quotestr):
        gallonstr, datestr, pricestr, *addrstr = quotestr.split("|")
        gallons = int(gallonstr)
        date = dtdate.fromisoformat(datestr)
        if(len(pricestr)==0):
            price = None
        else:
            price = float(pricestr)
        address = Address(*addrstr)
        return Quote(gallons, date, address, price)
    def __str__(self):
        return f"{self.gallons}|{self.date}|{self.price}|{self.address}"
    def __eq__(self, obj):
        return isinstance(obj, Quote) and self.gallons == obj.gallons and self.date == obj.date and self.price == obj.price and self.address == obj.address