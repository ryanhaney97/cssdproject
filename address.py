class Address:
	address_by_id = {}
	def __init__(self, city, state, zipcode, address1, address2=""):
		self.address1 = address1
		self.address2 = address2
		self.city = city
		self.state = state
		self.zipcode = zipcode
		self.id = None
	@property
	def id(self):
		return self.__id
	@id.setter
	def id(self, id):
		self.__id = id
		if(id is not None):
			Address.address_by_id[id] = self
	@staticmethod
	def from_str(addrstr):
		assert len(addrstr.split("|")) == 5
		return Address(*addrstr.split("|"))
	def __eq__(self, other):
		return isinstance(other, Address) and self.address1 == other.address1 and self.address2 == other.address2 and self.city == other.city and self.state == other.state and self.zipcode == other.zipcode
	def __str__(self):
		return f"{self.city}|{self.state}|{self.zipcode}|{self.address1}|{self.address2}"