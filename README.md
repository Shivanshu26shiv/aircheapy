<h2>aircheapy - returns cheapest flight-fare based on various parameters by scraping Happyeasygo.com</h2>

With aircheapy, you can get cheapest flight fares displayed on Happyeasygo.com - a travel portal for Indian users, where in its flight booking system, either one of the departure and arrival cities must be in India. Parameters to be used are as below:

	{
	'adults': 2,
	'cabinClass': 'Economy', # Economy, Business, First, Premium Economy
	'cheapest_N_results': 3,
	'depart_on_weekend': False,
	'from_IATA': {'BLR': 'Bengaluru'},
	'maxINR': 30000,
	'round_trip': True,
	'scan_till_N_days': 30,
	'to_IATA': {'BKK': 'Bangkok', 'DXB': 'Dubai'}
	
	# below 3 flags are ignored if round_trip flag is off
	'minGap': 3, # minimum gap between days of departure & arrival 
	# 'maxGap': 3, # maximum gap between days of departure & arrival 
	'arrive_on_weekend': True,
	}

P.S: need a fair internet connection to scrape data

<h3>Using it:</h3>
<ol>
<li>To use aircheapy, fork this github repo</li>
<li>Download the dependencies using requirements.txt</li>
<li>Run aircheapy.py after customising params dict</li>
</ol>

<h3>Compatibility:</h3>
aircheapy is compatible for python3.


<h3>Sample output:</h3>

	{
	'Bengaluru->Bangkok->Bengaluru': 
		[('05 March 2020 (Thursday) to 14 March 2020 (Saturday) '
		'[https://www.happyeasygo.com/flights/BLR-BKK/2020-03-05-2020-03-14?adults=2&cabinClass=Economy]',
		23810)]
	}

<h3>Contact:</h3>
<ul>
<li>LinkedIn: https://www.linkedin.com/in/shivanshu26shiv/</li>
</ul>
