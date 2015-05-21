#!/usr/bin/env python3

import hexchat
import urllib.request
import json
import threading

# Module details
__module_name__ = "where-are-you"
__module_version__ = "0.1"
__module_description__ = "Find the location of everyone joining the channel."

# Global variables
geoip_api = "https://freegeoip.net/json/"

def join_message_parser(word, word_eol, userdata):
	ip = word_eol[1].split("@")[1]
	temp = urllib.request.urlopen("{}{}".format(geoip_api, ip)).read()
	location = json.loads(temp.decode("utf-8"))
	print("\002\00304 ( {} ) Country: {} , Region: {} , City: {} , Time Zone: {} ".format(
		word[0], location['country_name'], location['region_name'], location['city'], location['time_zone'])
	)
	return hexchat.EAT_NONE

def thread(word, word_eol, userdata):
	threading.Thread(target=join_message_parser, args=(word, word_eol, userdata)).start()

print("\002%s is loading up .." % __module_name__)
hexchat.hook_print("Join", thread)
hexchat.hook_print("WhoIs Real Host", thread)
