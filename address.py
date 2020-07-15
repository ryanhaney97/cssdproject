class Address:
	address_by_id = {}
	def __init__(self, city, state, zipcode, address1, address2=""):
		self.address1 = address1
		self.address2 = address2
		self.city = city
		self.state = state
		self.zipcode = zipcode
		self.id = None
	def setID(self, id):
		self.id = id
		Address.address_by_id[id] = self
	def __eq__(self, other):
		return isinstance(other, Address) and self.address1 == other.address1 and self.address2 == other.address2 and self.city == other.city and self.state == other.state and self.zipcode == other.zipcode
	def __repr__(self):
		return str(self.address1) + "\n" + ((str(self.address2) + "\n") if len(str(self.address2))!=0 else "") + str(self.city) + ", " + str(self.state) + " " + str(self.zipcode) + "\n"