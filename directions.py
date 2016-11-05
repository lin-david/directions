import sys
import os
import webbrowser
import googlemaps
from datetime import datetime
import requests
import json

def make_html(all_legs):
    html_code = ''
    for leg in all_legs:
        all_steps = leg['steps']
        for step in all_steps:
            # Add direction instruction
            html_code += 'In ' + step['distance']['text'] + ': ' + step['html_instructions'] + '<br>'
            if step['travel_mode'] == 'TRANSIT':
                html_code += 'Use ' + step['transit_details']['line']['name'] + ' Line' + '<br>'
        html_code += 'Destination: ' + leg['end_address'] + '<br>' + '<br>'
    return html_code

# Remove API key if making app public
# Or use client ID if using Google Maps API's Premium Plan
key = 'AIzaSyB7vwusDtgJbI-pT608kav57um2MAQAwDw'
gmaps = googlemaps.Client(key)

print('This application will direct you to the nearest coffee shop, donut shop, and then to the ClickTime office in San Francisco!')
mode_transportation = input('Is your transportation mode walking, bicycling, or transit? ')

# Make sure that response is acceptable
while not (mode_transportation == 'walking' or mode_transportation == 'bicycling'
           or mode_transportation == 'transit'):
    if mode_transportation == 'quit':
        sys.exit()
    mode_transportation = input('Please enter walking, bicycling, transit, or quit: ')

destination = input('What is your desired destination name or address? ')
destination = gmaps.places(destination)['results'][0]['name']

# Get location from IP Address and Google Geocoding API
# Note: not accurate enough
r = requests.get('http://freegeoip.net/json')
loc_json = json.loads(r.text)
lat_lng = (loc_json['latitude'], loc_json['longitude'])
loc = reverse_geocode_result = gmaps.reverse_geocode(lat_lng)
approx_loc = loc[2]['formatted_address']

origin = approx_loc
now = datetime.now()

# Find coffee shop using Google Places API
coffee = gmaps.places('coffee', location=lat_lng, radius=1600)['results'][0]
donuts = gmaps.places('donuts', location=lat_lng, radius=1600)['results'][0]

wp = []
wp.append(coffee['formatted_address'])
wp.append(donuts['formatted_address'])
html = ''

# If using transit, walk to coffee and donut shop first, then transit to ClickTime
if mode_transportation == 'transit':
    directions_result = gmaps.directions(origin,
                                         wp[1],
                                         mode='walking',
                                         waypoints=[wp[0]],
                                         departure_time=now)
    html += make_html(directions_result[0]['legs'])
    origin = wp[1]
    wp = []

# Request directions via transportation mode using Google Directions API
directions_result = gmaps.directions(origin,
                                     destination,
                                     mode=mode_transportation,
                                     waypoints=wp,
                                     departure_time=now)

html += make_html(directions_result[0]['legs'])

# Formatting for HTML
header = '<html><head><title>Directions</title></head><body>' + 'Origin: ' + approx_loc + '<br>'
header += 'Coffee Shop: ' + coffee['name'] + '<br>' + 'Donuts Shop: ' + donuts['name'] + '<br>' + '<br>'
footer = '</body></html>'

# Formalize HTML code
html = header + html + footer

# Write HTML code to new file
html_file = open('index.html', 'w')
html_file.write(html)
html_file.close()

# Open HTML file in browser
path = os.path.abspath('index.html')
url = 'file://' + path
webbrowser.open(url)
