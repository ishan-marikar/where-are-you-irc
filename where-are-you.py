#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hexchat
import requests
import threading
import re
import sqlite3
import os

# Module details
__module_name__ = "where-are-you"
__module_version__ = "0.1"
__module_description__ = "Find the location of everyone joining the channel."

# Global variables
geoip_api = "https://freegeoip.net/json/"
channels_to_monitor = ["#mnfh"]

# The code that follows sucks. You know it and I know it.
# Move on and call me an idiot later.


def is_user_exists(user_info):
    with connect_database() as connection:
        current_cursor = connection.cursor()
        current_cursor.execute(
            """
            SELECT * FROM Users
            WHERE nickname= ?
            AND hostname = ?
            AND country = ?
            AND region = ?
            AND city = ?
            AND time_zone = ?
            AND latitude = ?
            AND longitude = ?
            AND channel = ? ;
            """,
            user_info
        )
        returned_values = current_cursor.fetchone()
        if returned_values is None:
            return False
        else:
            return True


def insert_user(user_info):
    # Add the user
    with connect_database() as connection:
        current_cursor = connection.cursor()
        current_cursor.execute(
            "INSERT INTO Users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            user_info
        )


def connect_database():
    db_filename = "users.db"
    database_schema = """
        CREATE TABLE Users (
            id INTEGER PRIMARY KEY ,
            nickname TEXT,
            hostname TEXT,
            country TEXT,
            region TEXT,
            city TEXT,
            time_zone TEXT,
            latitude TEXT,
            longitude TEXT,
            channel TEXT
        );
        """
    connection = None
    # Create the database and table if it does not exist
    if not os.path.exists(db_filename):
        connection = sqlite3.connect(db_filename)
        current_cursor = connection.cursor()
        current_cursor.executescript(database_schema)
        print("\002Creating database..")
    else:
        # .. or else, just open it.
        connection = sqlite3.connect(db_filename)

    return connection


# Here be dragons.
def geolocate_ip(hostname):
    complete_api_url = "{0}{1}".format(geoip_api, hostname)
    # Send the request to the API and parse the response
    response = requests.get(complete_api_url)
    location = response.json()
    # Loop through the  response and change any empty values to 'N/A'
    for element in location:
        if not location[element]:
            location[element] = "N/A"
    return location


def join_message_parser(word, word_eol, userdata):
    try:
        nickname = word[0]
        # Extract the ip-address/hostname and append it to the api url
        hostname = word_eol[1].split("@")[1].split()[0]

        """ Kiwiirc's source addresses (and most other
        web-based IRC clients) usually return this
        in place of the ip/hostname:

        'gateway/web/cgi-irc/kiwiirc.com/ip.127.0.0.1'

        .. which, ofcourse we can't pass to the API,
        so we look for an ip instead. """

        if "/" in hostname:
            ip_pattern = re.compile("[0-9]+(?:\.[0-9]+){3}")
            hostname = re.findall(ip_pattern, hostname)[0]

        # Geo-locate the ip/hostname
        location = geolocate_ip(hostname)

        # Print the message onto the Hexchat buffer and add to the database
        print(
            "\002\00304 ( {0} ) Country: {1} , Region: {2} , City: {3} , Time Zone: {4}".format(
                nickname,
                location['country_name'],
                location['region_name'],
                location['city'],
                location['time_zone']
            )
        )
        channel = hexchat.get_info('channel')
        if channel in channels_to_monitor:
            user_info = (
                nickname, hostname,
                location['country_name'],
                location['region_name'],
                location['city'],
                location['time_zone'],
                location['latitude'],
                location['longitude'],
                channel)
            if not is_user_exists(user_info):
                insert_user(user_info)

    except Exception as ex:
        pass

    return hexchat.EAT_NONE


def thread(word, word_eol, userdata):
    threading.Thread(
        target=join_message_parser,
        args=(word, word_eol, userdata)
    ).start()


print("\002%s is loading up .." % __module_name__)
hexchat.hook_print("Join", thread)
