#!/usr/bin/env python

import hexchat
import requests
import threading
import re

# Module details
__module_name__ = "where-are-you"
__module_version__ = "0.1"
__module_description__ = "Find the location of everyone joining the channel."

# Global variables
geoip_api = "https://freegeoip.net/json/"

def join_message_parser(word, word_eol, userdata):
	try:
		# Extract the ip-address/hostname and append it to the api url
		hostname = word_eol[1].split("@")[1]
		hostname = hostname.split()[0]
		# Kiwiirc's source addresses (and other web-based IRC clients) usually returns the hostname as:
		# "gateway/web/cgi-irc/kiwiirc.com/ip.127.0.0.1"
		# .. which usually screws with the api. We extract the IP because that is what we really need.
		if "/" in hostname:
			ip_pattern = re.compile("[0-9]+(?:\.[0-9]+){3}")
			hostname = re.findall(ip_pattern, hostname)
			hostname = hostname[0]
		complete_api_url = "{0}{1}".format(geoip_api, hostname)
		# Send the request to the API and parse the response
		response = requests.get(complete_api_url)
		location = response.json()
		# Loop through the  response and change any empty values to 'N/A'
		for element in location:
			if not location[element]:
				location[element] = "N/A"
		# Print the message onto the Hexchat buffer
		print(
			"\002\00304 ( {0} ) Country: {1} , Region: {2} , City: {3} , Time Zone: {4} ".format(
			word[0], location['country_name'], location['region_name'], location['city'], location['time_zone'])
		)
	except Exception as ex:
		pass

	return hexchat.EAT_NONE

def thread(word, word_eol, userdata):
	threading.Thread( target=join_message_parser, args=(word, word_eol, userdata) ).start()

print("\002%s is loading up .." % __module_name__)
hexchat.hook_print("Join", thread)
hexchat.hook_print("WhoIs Real Host", thread)
