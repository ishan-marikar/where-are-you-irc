#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hexchat
import re
# PyNaCl issues a warning every time it's imported
import requests

# Module details
__module_name__ = "where-are-you"
__module_version__ = "0.1"
__module_description__ = "Find the location of everyone joining the channel."

# Global variables
geoip_api = "https://freegeoip.net/json/"
ip_pattern = re.compile("[0-9]+(?:\.[0-9]+){3}")

def join_message_parser(word, word_eol, userdata):
	try:
		# Use the regex to find any IPs in the message
		# TODO: Searching for hostnames if we don't find any IPs
		ip = re.findall(ip_pattern, word_eol[0])
		# Loop through all the IPs and append the last one to the url
		for current_ip in ip:
			complete_url = geoip_api + current_ip
		# Send the request to the API and parse the response
		response = requests.get(complete_url)
		location = response.json()
		# Loop through the  response and change any empty values to 'N/A'
		for element in location:
			if not location[element]:
				location[element] = "N/A"
		# Print the message onto the Hexchat buffer
		print "\002\00304 ( %s ) Country: %s , Region: %s , City: %s , Time Zone: %s " % ( word[0], location['country_name'], location['region_name'], location['city'], location['time_zone'])

	except:
		# Silently pass through any errors (which is more likely to happen because sometimes
		# the thier host might not be their machine IP and more likely be a bouncer or what-not
		pass
	# Report back to Hexchat letting it know that it shouldn't do anything to the message we
	# intercepted in the buffer
	return hexchat.EAT_NONE

print "\002%s is loading up .." % __module_name__
hexchat.hook_print("Join", join_message_parser)
hexchat.hook_print("WhoIs Real Host", join_message_parser)

