def calc_full_quote(profile, quote):
	state = quote.address.state
	current_price_per_gallon = 1.50
	location_factor = .02 if state.upper() == "TX" else .04
	history_factor = 0 if len(profile.quotes) == 0 else .01
	gallon_factor = .02 if quote.gallons > 1000 else .03
	profit_factor = .1
	margin = current_price_per_gallon * (location_factor - history_factor + gallon_factor + profit_factor)
	quote.price = current_price_per_gallon + margin
	return quote.price