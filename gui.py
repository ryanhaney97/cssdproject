from address import Address
from quote import Quote
import webview
import os
import asyncio
import client_calls as call
from datetime import date as dtdate, datetime as dtdatetime

class Api:
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		self.profile = None
		self.error = None
		self.connected = False
	def login(self, username, password):
		if(not self.connected):
			self.loop.run_until_complete(call.connect())
			self.connected = True
		response = self.loop.run_until_complete(call.login(username, password))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def logout(self):
		if(self.connected):
			self.loop.run_until_complete(call.logout())
			self.profile = None
			self.quotes = None
			self.error = None
			self.connected = False
	def register(self, username, password, confpassword, name, addr1, addr2, city, state, zip):
		if(not self.connected):
			self.loop.run_until_complete(call.connect())
			self.connected = True
		if(password!=confpassword):
			return "Error: password does not match confirmed password"
		response = self.loop.run_until_complete(call.register(username, password, name, Address(city, state, zip, addr1, addr2)))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def getquotefor(self, gallons, sdate):
		try:
			igallons = int(gallons)
		except ValueError:
			return "Error: " + gallons + " is not a number"
		date = dtdatetime.strptime(sdate, "%m/%d/%Y").date()
		self.profile.quoteinprogress = Quote(igallons, date, self.profile.address)
		result = self.loop.run_until_complete(call.get_quote(self.profile.quoteinprogress.gallons, self.profile.quoteinprogress.date))
		if(isinstance(result, float)):
			self.profile.quoteinprogress.price = result
			return "Success"
		return result
	def editprofile(self, name, addr1, addr2, city, state, zip, oldpassword, newpassword, confnewpassword):
		if(newpassword!=confnewpassword):
			return "Error: new password does not match confirmed new password"
		addr = Address(city, state, zip, addr1, addr2)
		changes = {}
		if(addr!=self.profile.address and len(addr1)!=0 and len(city)!=0 and len(state)!=0 and len(zip)!=0):
			changes["address"] = addr
		if(name!=profile.name and len(name)!=0):
			changes["name"] = name
		if(len(oldpassword)!=0):
			changes["oldpassword"] = oldpassword
		if(len(newpassword)!=0):
			changes["newpassword"] = newpassword
		if(len(changes.keys()) == 0):
			return "No changes made"
		response = self.loop.run_until_complete(call.update_profile(**changes))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def submitquote(self):
		return self.loop.run_until_complete(call.submit_quote())
	def getquotehistory(self):
		self.profile.quotes = self.loop.run_until_complete(call.get_quote_history())
		quotes = []
		for quote in self.profile.quotes:
			quotes.append({"gallons": quote.gallons,
						   "date": str(quote.date),
						   "price": quote.price,
						   "total": quote.total,
						   "address": {"address1": quote.address.address1,
						   			   "address2": quote.address.address2,
						   			   "city": quote.address.city,
						   			   "state": quote.address.state,
						   			   "zipcode": quote.address.zipcode}})
		print(quotes)
		return quotes
	def getprice(self):
		return self.profile.quoteinprogress.price
	def gettotal(self):
		return self.profile.quoteinprogress.total
	def getname(self):
		if(self.profile is None):
			return None
		return self.profile.name
	def getusername(self):
		if(self.profile is None):
			return None
		return self.profile.username
	def getaddress1(self):
		if(self.profile is None):
			return None
		return self.profile.address.address1
	def getaddress2(self):
		if(self.profile is None):
			return None
		return self.profile.address.address2
	def getcity(self):
		if(self.profile is None):
			return None
		return self.profile.address.city
	def getstate(self):
		if(self.profile is None):
			return None
		return self.profile.address.state
	def getzipcode(self):
		if(self.profile is None):
			return None
		return self.profile.address.zipcode

def main():
	api = Api()
	window = webview.create_window("CS Project", url="login.html", js_api = api)
	window.closing += api.logout
	webview.start(debug=True)

if __name__ == "__main__":
    main()
