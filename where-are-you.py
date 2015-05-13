#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hexchat
import re
# PyNaCl issues a warning every time it's imported
import requests

__module_name__ = "where-are-you"
__module_version__ = "0.1"
__module_description__ = "Find the location of everyone joining the channel."

geoip_api = "https://freegeoip.net/json/"
ip_pattern = re.compile("[0-9]+(?:\.[0-9]+){3}")

def join_message_parser(word, word_eol, userdata):
	try:
		ip = re.findall(ip_pattern, word_eol[0])
		complete_url = geoip_api + ip[0]
		response = requests.get(complete_url)
		location = response.json()
		print "\002\00304 ( %s ) Country: %s , Region: %s , City: %s , Time Zone: %s " % ( word[0], location['country_name'], location['region_name'], location['city'], location['time_zone'])
	except:
		pass
	
	return hexchat.EAT_NONE

print "\002%s is loading up .." % __module_name__
hexchat.hook_print("Join", join_message_parser)
hexchat.hook_print("WhoIs Real Host", join_message_parser)

