from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from address import Address
from quote import Quote
import webview
import os
import asyncio
import client_calls as call

app = Flask(__name__)

class Api:
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		self.profile = None
		self.error = None
		self.loop.run_until_complete(call.connect())
	def login(self, username, password):
		response = self.loop.run_until_complete(call.login(username, password))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def logout(self):
		self.loop.run_until_complete(call.logout())
		self.profile = None
		self.quotes = None
		self.error = None
	def register(self, username, password, confpassword, name, addr1, addr2, city, state, zip):
		if(password!=confpassword):
			return "Error: password does not match confirmed password"
		response = self.loop.run_until_complete(call.register(username, password, name, Address(city, state, zip, addr1, addr2)))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def getquotefor(self, gallons, date):
		self.profile.quoteinprogress = Quote(int(gallons), date, self.profile.address)
		self.profile.quoteinprogress.price = float(self.loop.run_until_complete(call.get_quote(gallons, date)))
		return self.profile.quoteinprogress.price
	def submitquote(self):
		return self.loop.run_until_complete(call.submit_quote())
	def getquotehistory(self):
		self.profile.quotes = self.loop.run_until_complete(call.get_quote_history())
		return self.profile.quotes
	def getprice(self):
		return self.quote.price
	def gettotal(self):
		return self.quote.total 
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

@app.route('/register')
def registration():
	return render_template('registration.html')

@app.route('/')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run()
